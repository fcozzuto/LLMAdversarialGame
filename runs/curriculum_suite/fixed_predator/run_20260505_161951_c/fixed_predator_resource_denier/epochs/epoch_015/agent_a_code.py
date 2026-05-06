def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    ob = set((a, b) for a, b in obstacles)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in ob

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        # Drift to maximize separation; deterministic tie-break favors staying toward far corner.
        best = (-(10**9), 0, 0)
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if not valid(nx, ny): 
                continue
            sep = cheb(nx, ny, ox, oy)
            far_corner = abs(nx - (w - 1)) + abs(ny - (h - 1))
            val = (sep, -far_corner, -dx, -dy)
            if val > best:
                best = val
                ret = [dx, dy]
        return ret

    # Evaluate possible next cells by how much they deny opponent access while still advancing to a resource.
    best = None
    # precompute for tie-break
    res_list = resources[:]
    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not valid(nx, ny):
            continue
        # pick a target resource where we are relatively advantaged after the move
        best_r = None
        for rx, ry in res_list:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # If we can reach much sooner than opponent, high value; also prefer making closest resource even closer.
            v = (do - ds) * 1000 - ds
            if best_r is None or v > best_r[0] or (v == best_r[0] and (rx, ry) < best_r[1]):
                best_r = (v, (rx, ry))
        # diversify: prefer not being equally bad against all resources (use min ds)
        min_ds = None
        for rx, ry in res_list:
            ds = cheb(nx, ny, rx, ry)
            if min_ds is None or ds < min_ds:
                min_ds = ds
        # penalty if opponent can also quickly reach many resources: approximate by avg of (cheb(opp, r) - cheb(self_next, r))
        denial = 0
        for rx, ry in res_list:
            denial += cheb(ox, oy, rx, ry) - cheb(nx, ny, rx, ry)
        val = (best_r[0], denial, -min_ds, -abs(nx - (w - 1)) - abs(ny - (h - 1)), -dx, -dy)
        if best is None or val > best[0]:
            best = (val, [dx, dy])

    return best[1]