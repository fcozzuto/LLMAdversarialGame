def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    gw, gh = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < gw and 0 <= y < gh

    def legal(x, y):
        return in_bounds(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    def neigh_count(x, y):
        c = 0
        for dx, dy in moves:
            nx, ny = x + dx, y + dy
            if legal(nx, ny):
                c += 1
        return c

    # If no resources, drift toward center while keeping options (avoid being trapped by obstacles).
    if not resources:
        cx, cy = (gw - 1) // 2, (gh - 1) // 2
        best = (0, 0, -10**9)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = cheb(nx, ny, cx, cy)
            v = -d + 0.4 * neigh_count(nx, ny)
            if v > best[2]:
                best = (dx, dy, v)
        return [best[0], best[1]]

    # Choose best move toward closest resource; add strong bias to prevent opponent stealing if they are closer.
    best = (0, 0, -10**18)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        # immediate pickup advantage: if stepping onto a resource, heavily reward
        if (nx, ny) in resources:
            v = 10**6 + 10 * neigh_count(nx, ny) - 0.01 * cheb(nx, ny, ox, oy)
            if v > best[2]:
                best = (dx, dy, v)
            continue

        my_best = 10**9
        opp_best = 10**9
        for rx, ry in resources:
            d_my = cheb(nx, ny, rx, ry)
            if d_my < my_best:
                my_best = d_my
            d_op = cheb(ox, oy, rx, ry)
            if d_op < opp_best:
                opp_best = d_op

        # If opponent is already closer to the nearest resources, we try to "intercept" by reducing opp_best too.
        # Strongly penalize moving toward/near opponent when resources are still abundant.
        dist_opp = cheb(nx, ny, ox, oy)
        richness = observation.get("remaining_resource_count", len(resources))
        danger = 0.0
        if richness >= 6 and dist_opp <= 2:
            danger = 80.0 / (1 + dist_opp)

        v = (-my_best) + 0.6 * neigh_count(nx, ny) + (-0.35 * opp_best) - danger + 0.01 * dist_opp
        if v > best[2]:
            best = (dx, dy, v)

    return [best[0], best[1]]