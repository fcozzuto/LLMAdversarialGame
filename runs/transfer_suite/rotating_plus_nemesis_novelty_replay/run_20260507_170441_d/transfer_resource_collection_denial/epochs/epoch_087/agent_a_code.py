def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obst = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obst.add((p[0], p[1]))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def md(x1, y1, x2, y2):
        d = x1 - x2
        if d < 0:
            d = -d
        e = y1 - y2
        if e < 0:
            e = -e
        return d + e

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            nx, ny = sx, sy
        my_best = 10**18
        opp_best = 10**18
        for r in resources:
            rx, ry = r[0], r[1]
            myd = md(nx, ny, rx, ry)
            oppd = md(ox, oy, rx, ry)
            if myd < my_best:
                my_best = myd
            if oppd < opp_best:
                opp_best = oppd
        # Prefer moves that get closer, especially to resources where we are ahead.
        score = (opp_best - my_best) * 1000 - my_best
        if score > best_score:
            best_score = score
            best = (dx, dy)
        elif score == best_score:
            # deterministic tie-break: prefer not moving, then lexicographic dx,dy
            if (dx, dy) == (0, 0) and best != (0, 0):
                best = (dx, dy)
            elif best is not None and (dx, dy) < best:
                best = (dx, dy)

    dx, dy = best
    return [dx, dy]