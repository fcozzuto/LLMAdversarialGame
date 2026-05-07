def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            moves.append((dx, dy))
    if not moves:
        return [0, 0]

    if resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            dres = min(abs(nx - rx) + abs(ny - ry) for rx, ry in resources)
            dop = abs(nx - ox) + abs(ny - oy)
            key = (dres, -dop, dx, dy)
            if best is None or key < best[0]:
                best = (key, (dx, dy))
        return [best[1][0], best[1][1]]

    tx, ty = (w - 1) // 2, (h - 1) // 2
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        d = abs(nx - tx) + abs(ny - ty)
        key = (d, abs(nx - ox) + abs(ny - oy), dx, dy)
        if best is None or key < best[0]:
            best = (key, (dx, dy))
    return [best[1][0], best[1][1]]