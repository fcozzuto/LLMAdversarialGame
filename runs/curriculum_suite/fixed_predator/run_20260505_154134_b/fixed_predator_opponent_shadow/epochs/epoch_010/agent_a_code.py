def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obs

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        # No resources: move to maximize distance from opponent (escape from shadow)
        best = [0, 0]
        bestv = -10**18
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    # Move selection: for each reachable move, pick the resource that maximizes a deterministic utility
    # utility favors being closer than opponent; tie-breaker on absolute closeness.
    best_move = [0, 0]
    best_val = -10**18
    # Precompute for stability
    res_list = [(r[0], r[1]) for r in resources if isinstance(r, (list, tuple)) and len(r) >= 2]

    for dxm, dym in dirs:
        nx, ny = sx + dxm, sy + dym
        if not valid(nx, ny):
            continue
        best_for_move = -10**18
        for cx, cy in res_list:
            self_d = cheb(nx, ny, cx, cy)
            opp_d = cheb(ox, oy, cx, cy)
            # Positive when we are closer; small term encourages faster absolute arrival.
            util = (opp_d - self_d) * 100 - self_d
            # If opponent is closer/equal, still allow blocking by maximizing (opp_d - self_d) and closeness to future.
            if util > best_for_move:
                best_for_move = util
        # Small preference for moves that also improve our general position (closer to best res from current)
        cur_best = -10**18
        for cx, cy in res_list:
            self_d0 = cheb(sx, sy, cx, cy)
            opp_d0 = cheb(ox, oy, cx, cy)
            util0 = (opp_d0 - self_d0) * 100 - self_d0
            if util0 > cur_best:
                cur_best = util0
        # Reward improvement over current best utility to avoid dithering
        val = best_for_move + (best_for_move - cur_best) * 0.01
        if val > best_val:
            best_val = val
            best_move = [dxm, dym]

    return best_move