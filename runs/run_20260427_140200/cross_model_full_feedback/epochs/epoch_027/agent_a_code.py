def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position") or [0, 0]
    opp = observation.get("opponent_position") or [0, 0]
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obs = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    resources = []
    for r in (observation.get("resources", []) or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if free(x, y):
                resources.append((x, y))

    def md(a, b, c, d):
        return abs(a - c) + abs(b - d)

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
        bestd = None
        for x, y in resources:
            d = md(sx, sy, x, y)
            if bestd is None or d < bestd:
                bestd = d
                target = (x, y)
        if target is None:
            target = resources[0]

    best_move = None
    best_score = None
    for dx, dy, nx, ny in sorted(legal, key=lambda t: (t[0], t[1])):
        score = 0
        if target is not None:
            myd = md(nx, ny, target[0], target[1])
            opd = md(nx, ny, ox, oy)
            score += 1000 - myd * 10
            score += -opd
            score += (5 if md(nx, ny, ox, oy) < md(sx, sy, ox, oy) else 0)
        else:
            score = -md(nx, ny, ox, oy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]