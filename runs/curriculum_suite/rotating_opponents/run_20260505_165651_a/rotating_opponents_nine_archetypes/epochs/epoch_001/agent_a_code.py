def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx if dx >= 0 else -dx if dx < 0 else -dx

    def dist_to_nearest(px, py):
        if not resources:
            return 0
        best = 10**9
        for rx, ry in resources:
            d = abs(px - rx)
            e = abs(py - ry)
            v = d if d > e else e
            if v < best:
                best = v
        return best

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]
    best_u = -10**18
    best = (0, 0)

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        collected = 1 if (nx, ny) in set(tuple(r) for r in resources) else 0
        our_dist = dist_to_nearest(nx, ny)

        # Opponent proxy: assume opponent stays (deterministic) and use their nearest distance from current pos.
        # Slightly prefer moves that do not let resources get closer to them quickly by moving toward resources.
        opp_dist = dist_to_nearest(ox, oy)

        # Utility: collect first, then minimize our distance, then keep opponent away.
        u = collected * 1000 - our_dist * 10 + opp_dist * 2
        if u > best_u or (u == best_u and (dx, dy) < best):
            best_u = u
            best = (dx, dy)

    return [best[0], best[1]]