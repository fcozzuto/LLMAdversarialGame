def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position") or [0, 0]
    opp = observation.get("opponent_position") or [0, 0]
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if free(x, y):
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    target = None
    if resources:
        best = None
        for rx, ry in resources:
            myd = abs(rx - sx) + abs(ry - sy)
            opd = abs(rx - ox) + abs(ry - oy)
            adv = (opd - myd, -myd, rx, ry)
            if best is None or adv > best:
                best = adv
                target = (rx, ry)
    else:
        target = (ox, oy)

    best_move = None
    best_score = None
    for dx, dy, nx, ny in legal:
        d_to_t = abs(target[0] - nx) + abs(target[1] - ny)
        d_opp = abs(ox - nx) + abs(oy - ny)
        score = (-(d_to_t), d_opp, dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]