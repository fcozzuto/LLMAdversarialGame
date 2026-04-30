def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [7, 7])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0:
            dx = -dx
        dy = a[1] - b[1]
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_move = [0, 0]

    opp_here = (ox, oy)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        me_next = (nx, ny)

        my_d = 10**9
        opp_d = 10**9
        for r in res:
            d = cheb(me_next, r)
            if d < my_d:
                my_d = d
        for r in res:
            d = cheb(opp_here, r)
            if d < opp_d:
                opp_d = d

        # If we're closer to some resource than opponent is (currently), prioritize getting even closer.
        # Also discourage moves that let opponent keep parity (defensive stance).
        gap = opp_d - my_d

        # Tie-breakers: prefer larger gap; if still tied, prefer moving toward resources with smaller sum distance;
        # else prefer staying away from opponent.
        min_sum = 10**9
        for r in res:
            d = cheb(me_next, r) + cheb(opp_here, r)
            if d < min_sum:
                min_sum = d

        # Negative because we want lexicographically maximum gap, then minimum my_d, then minimum min_sum, then max distance from opponent.
        dist_from_opp = cheb(me_next, opp_here)

        key = (gap, -my_d, -min_sum, dist_from_opp, -dx, -dy)
        if best is None or key > best:
            best = key
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]