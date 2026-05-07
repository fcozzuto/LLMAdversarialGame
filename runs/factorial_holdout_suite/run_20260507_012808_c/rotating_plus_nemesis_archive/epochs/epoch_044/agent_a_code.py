def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])

    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not res:
        best = [0, 0]
        best_val = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            v = -cheb(nx, ny, ox, oy)
            if v > best_val:
                best_val = v
                best = [dx, dy]
        return best

    opp_best = cheb(ox, oy, res[0][0], res[0][1])
    for rx, ry in res[1:]:
        d = cheb(ox, oy, rx, ry)
        if d < opp_best:
            opp_best = d

    best = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        my_best = cheb(nx, ny, res[0][0], res[0][1])
        for rx, ry in res[1:]:
            d = cheb(nx, ny, rx, ry)
            if d < my_best:
                my_best = d
        my_to_opp = cheb(nx, ny, ox, oy)
        # Maximize arrival advantage over opponent; break ties by faster arrival and slight separation.
        v = (opp_best - my_best) * 10 - my_best - my_to_opp * 0.1
        if v > best_val:
            best_val = v
            best = [dx, dy]

    return best