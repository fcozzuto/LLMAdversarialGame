def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                moves.append((dx, dy))

    # Fallback: drift to farther corner from opponent while avoiding obstacles
    if not moves or not resources:
        tx = (0 if sx > w // 2 else w - 1)
        ty = (0 if sy > h // 2 else h - 1)
        best = [0, 0]
        bestv = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            v = (abs(tx - nx) + abs(ty - ny), abs(ox - nx) + abs(oy - ny))
            if bestv is None or v < bestv:
                bestv = v
                best = [dx, dy]
        return best

    def cell_value(x, y):
        # Prefer resources we can reach earlier than opponent; avoid opponent row/column (sweep-row pressure)
        best = None
        for rx, ry in resources:
            sd = abs(rx - x) + abs(ry - y)
            od = abs(rx - ox) + abs(ry - oy)
            row_pen = 0 if ry != oy else 3
            col_pen = 0 if rx != ox else 2
            # Smaller is better: our lead first, then faster capture, then global safety
            v = (sd - od + row_pen + col_pen, sd + 0.5 * od)
            if best is None or v < best:
                best = v
        # If no resource beats others, still keep stable choice
        return best

    # Choose move that maximizes our eventual advantage immediately
    best_move = [0, 0]
    best_v = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        v = cell_value(nx, ny)
        # lexicographic minimization on v
        if best_v is None or v < best_v:
            best_v = v
            best_move = [dx, dy]

    return best_move