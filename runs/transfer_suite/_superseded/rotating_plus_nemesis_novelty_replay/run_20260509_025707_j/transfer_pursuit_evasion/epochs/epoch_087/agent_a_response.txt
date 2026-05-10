def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for t in observation.get("obstacles") or []:
        if isinstance(t, (list, tuple)) and len(t) >= 2:
            x, y = int(t[0]), int(t[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def score(nx, ny):
        dx = nx - ox
        dy = ny - oy
        d = dx * dx + dy * dy
        # If stepping adjacent diagonal risks obstacle traps, prefer orthogonal when close.
        adj = 1 if (abs(dx) <= 1 and abs(dy) <= 1) else 0
        diag = 1 if (nx != sx and ny != sy) else 0
        # Small bias to reduce opponent mobility: avoid moving into long corridor directions.
        # Estimate local openness by counting free neighbors.
        open_cnt = 0
        for mx, my in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
            px, py = nx + mx, ny + my
            if 0 <= px < w and 0 <= py < h and (px, py) not in obstacles:
                open_cnt += 1
        return d + (0.6 * diag) + (0.15 * (8 - open_cnt)) - (0.05 * adj)

    best = None
    best_s = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        s = score(nx, ny)
        if best_s is None or s < best_s:
            best_s = s
            best = (dx, dy)

    if best is not None:
        return [int(best[0]), int(best[1])]

    # All moves blocked; deterministically try staying put.
    return [0, 0]