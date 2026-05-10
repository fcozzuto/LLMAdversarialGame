def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    if not resources:
        return [0, 0]

    # Heuristic: maximize resource control (closer than opponent), prefer immediate collection.
    res = [(int(p[0]), int(p[1])) for p in resources]
    best = None
    best_val = None
    for dx0, dy0 in deltas:
        nsx, nsy = sx + dx0, sy + dy0
        if not inb(nsx, nsy):
            nsx, nsy = sx, sy

        # Value depends on best reachable resource.
        my_best = 10**9
        opp_best = 10**9
        my_pick = None

        for rx, ry in res:
            dm = cheb(nsx, nsy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # small tie-break favoring earlier in scan order
            if dm < my_best:
                my_best, my_pick = dm, (rx, ry)
            if do < opp_best:
                opp_best = do

        # Opponent next-step approximation: they move to reduce distance to our best resource.
        rx, ry = my_pick
        o_step = None
        o_best = 10**9
        for odx, ody in deltas:
            nox, noy = ox + odx, oy + ody
            if not inb(nox, noy):
                nox, noy = ox, oy
            d = cheb(nox, noy, rx, ry)
            if d < o_best:
                o_best = d
                o_step = (nox, noy)

        dm_now = my_best
        do_next = cheb(o_step[0], o_step[1], rx, ry) if o_step else cheb(ox, oy, rx, ry)

        # If we land on a resource, strongly commit.
        collect_bonus = 0
        if (nsx, nsy) == (rx, ry):
            collect_bonus = 1000

        # Score: prefer smaller dm, but also avoid where opponent is closer next.
        # Larger is better.
        val = collect_bonus + (opp_best - dm_now) * 10 - do_next * 2

        if best_val is None or val > best_val or (val == best_val and (dx0, dy0) < best):
            best_val = val
            best = (dx0, dy0)

    return [int(best[0]), int(best[1])]