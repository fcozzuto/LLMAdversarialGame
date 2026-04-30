def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def score_cell(x, y):
        d = abs(x - sx) + abs(y - sy)
        adv = 0
        if (sx, sy) != (x, y):
            adv = -abs(x - ox) - abs(y - oy)
        return d + adv

    best = None
    best_sd = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        if resources:
            sd = min(abs(nx - rx) + abs(ny - ry) for (rx, ry) in resources)
        else:
            cx, cy = (w - 1) // 2, (h - 1) // 2
            sd = abs(nx - cx) + abs(ny - cy)
        tie = score_cell(nx, ny)
        key = (sd, tie, dx, dy)
        if best is None or key < best_sd:
            best = (dx, dy)
            best_sd = key

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]