def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def md(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    best = (-10**18, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h or (nx, ny) in obstacles:
            continue

        our_min = 10**9
        opp_min = 10**9
        for rx, ry in resources:
            d_ou = md(nx, ny, rx, ry)
            if d_ou < our_min:
                our_min = d_ou
            d_op = md(ox, oy, rx, ry)
            if d_op < opp_min:
                opp_min = d_op

        # Interception/denial: prefer moves where we can reach the opponent-targeted resource
        # sooner than opponent (or at least reduce the gap).
        # Opponent archetype: nearest_resource -> its target is current closest resource.
        tx, ty = resources[0]
        best_t = 10**9
        for rx, ry in resources:
            d = md(ox, oy, rx, ry)
            if d < best_t:
                best_t = d
                tx, ty = rx, ry
        d_ours = md(nx, ny, tx, ty)
        d_op = md(ox, oy, tx, ty)

        # Also nudge toward resources that are not closest to the opponent (spreads out threats).
        spread = 0
        for rx, ry in resources:
            da = md(nx, ny, rx, ry)
            db = md(ox, oy, rx, ry)
            if da < our_min + 2 and db > opp_min:
                spread += 1

        # Final heuristic: maximize denial and interception, with slight spread encouragement.
        key = (opp_min - our_min) * 20 + (d_op - d_ours) * 8 + spread

        # Tie-break deterministically by closeness to center of grid, then lexicographic move.
        cx, cy = w // 2, h // 2
        center_bias = -md(nx, ny, cx, cy)
        key2 = (key, center_bias)

        if key2 > (best[0], best[1]):
            best = (key2[0], key2[1], 0)
            best_dx, best_dy = dx, dy

    return [best_dx, best_dy]