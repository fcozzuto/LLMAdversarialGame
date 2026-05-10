def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            t = (int(p[0]), int(p[1]))
            if t not in obs:
                res.append(t)
    if not res:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    best_move = [0, 0]
    best_key = (-10**18, -10**9, -10**9)  # (advantage, -oppDist, -myDist)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        # Evaluate by best resource we can contest: maximize (oppDist - myDist).
        # Tie-break toward closer resources and away from giving opponent immediate progress.
        best_adv = -10**18
        best_res_dist_my = 10**9
        best_opp_dist = 10**9
        for rx, ry in res:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            adv = opd - myd
            if adv > best_adv or (adv == best_adv and (myd < best_res_dist_my or (myd == best_res_dist_my and opd < best_opp_dist))):
                best_adv = adv
                best_res_dist_my = myd
                best_opp_dist = opd

        # Prefer moves that also reduce our nearest overall distance slightly.
        my_nearest = min(cheb(nx, ny, rx, ry) for rx, ry in res)

        key = (best_adv, -best_opp_dist, -(my_nearest))
        if key > best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move