def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    raw_obs = observation.get("obstacles") or []
    obstacles = set()
    for p in raw_obs:
        if p is not None and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    res = []
    for r in resources:
        if r is not None and len(r) >= 2:
            x, y = r[0], r[1]
            if (x, y) not in obstacles:
                res.append((x, y))
    if not res:
        return [0, 0]
    res_set = set(res)

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_score = -10**18

    # Precompute opponent distances to each resource
    opp_d = {}
    for rx, ry in res:
        opp_d[(rx, ry)] = cheb(ox, oy, rx, ry)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        # If landing on resource, strongly prefer it
        hit = 1 if (nx, ny) in res_set else 0

        # Choose "race" target resource: maximize margin (opp_time - my_time)
        # Use Chebyshev as movement speed estimate.
        best_margin = -10**9
        best_my = 10**9
        for rx, ry in res:
            my_t = cheb(nx, ny, rx, ry)
            opp_t = opp_d[(rx, ry)]
            margin = opp_t - my_t
            if margin > best_margin or (margin == best_margin and my_t < best_my):
                best_margin = margin
                best_my = my_t

        # Also encourage moving away from opponent (denier archetype) a bit
        d_opp = cheb(nx, ny, ox, oy)

        # Score: prioritize immediate pickup, then maximize race margin and closeness.
        score = (10.0 * hit) + (2.0 * best_margin) - (0.08 * best_my) + (0.03 * d_opp)

        if score > best_score or (score == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score
            best_move = [dx, dy]

    return best_move