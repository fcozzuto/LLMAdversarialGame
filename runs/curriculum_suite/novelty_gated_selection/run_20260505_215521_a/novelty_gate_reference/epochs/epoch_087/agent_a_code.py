def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    sx, sy = int(sx), int(sy)
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y):
                resources.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    ox, oy = int(ox), int(oy)

    if resources:
        def score_cell(x, y):
            d = abs(x - sx) + abs(y - sy)
            od = abs(x - ox) + abs(y - oy)
            return (d - 0.7 * od, d, (x + y) % 2)
        tx, ty = min(resources, key=lambda p: score_cell(p[0], p[1]))

        best = None
        best_val = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            v = (abs(nx - tx) + abs(ny - ty), abs(nx - ox) + abs(ny - oy), (nx + ny) % 2, dx, dy)
            if best_val is None or v < best_val:
                best_val = v
                best = [dx, dy]
        if best is not None:
            return best

    # Fallback: move toward staying in bounds while not going closer to opponent too much
    best = [0, 0]
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        v = (abs(nx - ox) + abs(ny - oy), abs(nx - (w // 2)) + abs(ny - (h // 2)), dx, dy)
        if best_val is None or v > best_val:
            best_val = v
            best = [dx, dy]
    return best