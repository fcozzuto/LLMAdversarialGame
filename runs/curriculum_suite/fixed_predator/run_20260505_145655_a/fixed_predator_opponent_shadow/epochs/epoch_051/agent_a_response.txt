def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def clamp_step(dx, dy):
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny):
            return x, y
        if (nx, ny) in obstacles:
            return x, y
        return nx, ny

    def dist(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if not resources:
        dx = sign(ox - x)
        dy = sign(oy - y)
        return [dx, dy]

    # Move evaluation: one-step lookahead toward best resource by advantage over opponent.
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = -10**18

    for dx, dy in deltas:
        nx, ny = clamp_step(dx, dy)
        # Prefer resources where we are closer than opponent, especially if opponent is also close.
        best_resource_val = -10**18
        for tx, ty in resources:
            d_me = dist(nx, ny, tx, ty)
            d_opp = dist(ox, oy, tx, ty)
            lead = d_opp - d_me
            # Strongly reward being ahead; mildly prefer nearer resources and bigger lead margins.
            val = lead * 1200 - d_me + 0.01 * d_opp
            if val > best_resource_val:
                best_resource_val = val

        # Tie-breaker: avoid letting opponent immediately become much closer to their nearest resource.
        opp_nearest = min(dist(ox, oy, tx, ty) for tx, ty in resources)
        my_nearest = min(dist(nx, ny, tx, ty) for tx, ty in resources)
        val = best_resource_val - 8.0 * max(0.0, my_nearest - opp_nearest)

        if val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    return [best[0], best[1]]