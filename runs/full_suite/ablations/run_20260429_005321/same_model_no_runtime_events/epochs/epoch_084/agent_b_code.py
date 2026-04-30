def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if ok(x, y):
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not ok(sx, sy):
        for dx, dy in dirs:
            if ok(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    def score_move(nx, ny):
        # prefer moves that get closer to nearest resource; if none, closer to opponent
        if resources:
            best = 10**9
            for rx, ry in resources:
                d = abs(nx - rx) if abs(nx - rx) >= abs(ny - ry) else abs(ny - ry)
                if d < best:
                    best = d
            return -best
        d = abs(nx - ox) if abs(nx - ox) >= abs(ny - oy) else abs(ny - oy)
        return -d

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        v = score_move(nx, ny)
        # deterministic tie-break: prefer non-zero moves in fixed order
        if v > best_val or (v == best_val and (dx, dy) > tuple(best_move)):
            best_val = v
            best_move = [dx, dy]
    return best_move