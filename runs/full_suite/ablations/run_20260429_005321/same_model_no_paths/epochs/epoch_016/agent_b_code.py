def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inside(x, y) and (x, y) not in obstacles

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    def min_dist_to_resources(x, y):
        if not resources: return 10**9
        m = None
        for rx, ry in resources:
            d = cheb(x, y, rx, ry)
            if m is None or d < m: m = d
        return m if m is not None else 10**9

    if any(sx == rx and sy == ry for rx, ry in resources):
        return [0, 0]

    def obstacle_adj_penalty(x, y):
        p = 0
        for dx, dy in deltas:
            if (x + dx, y + dy) in obstacles:
                p += 1
        return p

    # Evaluate each candidate by prioritizing resources where we are closer than opponent,
    # and otherwise avoid enabling opponent by moving away from the opponent's best resource.
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny): 
            continue

        myd = min_dist_to_resources(nx, ny)
        if myd == 10**9:
            myd = 20

        # pick opponent's nearest resource and compare reachability
        if resources:
            om = None
            for rx, ry in resources:
                d = cheb(ox, oy, rx, ry)
                if om is None or d < om: om = d
            oppd = om if om is not None else 20
        else:
            oppd = 20

        # If there's a resource where opponent is closer than us, we penalize moves that keep us behind.
        reach_pen = 0
        if resources:
            worst = 0
            best_gap = -10**9
            for rx, ry in resources:
                d_s = cheb(nx, ny, rx, ry)
                d_o = cheb(ox, oy, rx, ry)
                gap = d_o - d_s  # positive means we are closer
                if gap > best_gap: best_gap = gap
                if gap < 0 and d_o <= d_s + 1:
                    worst += 1
            reach_pen = worst * 4

        # Interference: prefer reducing distance to opponent when we are already committed toward a resource?
        # Keep simple/deterministic: small term to avoid being trapped by opponent near us.
        opp_self = cheb(nx, ny, ox, oy)

        val = 0
        val += -2.2 * myd
        val += 0.9 * (oppd - myd)  # being closer than opponent to some resource is good
        val += -0.8 * opp_self
        val += -1.5 * obstacle_adj_penalty(nx, ny)
        val += -reach_pen
        val += 0.05 * min_dist_to_resources(ox, oy) if resources else 0  # deterministic mild tie

        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]