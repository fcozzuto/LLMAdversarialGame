def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    resources = [tuple(r) for r in (observation.get("resources") or []) if (0 <= r[0] < w and 0 <= r[1] < h)]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_score = -10**18

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def mhed(a, b, c, d):
        return abs(a - c) + abs(b - d)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    if not resources:
        tx = 0 if sx == cx else (1 if sx < cx else -1)
        ty = 0 if sy == cy else (1 if sy < cy else -1)
        return [tx, ty]

    # One-step lookahead: choose move maximizing expected capture advantage for best reachable resource.
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # For each resource: our "lead" (opponent time - self time) and fallback progress.
        local_best = -10**18
        local_second = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            self_t = mhed(nx, ny, rx, ry)
            opp_t = mhed(ox, oy, rx, ry)
            # Strong preference for resources where we can arrive sooner.
            lead = opp_t - self_t
            # Encourage moving toward the resource and slightly away from opponent.
            progress = -self_t - 0.15 * mhed(nx, ny, ox, oy)
            val = 6.0 * lead + progress
            # Tie-break deterministically by preferring smaller self_t then resource order.
            if val > local_best:
                local_second = local_best
                local_best = val
            elif val > local_second:
                local_second = val

        # If we can't beat opponent anywhere, shift to blocking-ish: reduce opponent's best potential.
        # Approx: opponent advantage if it took best resource from opponent position.
        opp_best = 10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            opp_best = min(opp_best, mhed(ox, oy, rx, ry))
        center_bias = -0.05 * ((nx - cx) * (nx - cx) + (ny - cy) * (ny - cy))
        cap_bias = local_best
        # Extra term encourages making our nearest-resource distance as small as possible.
        nearest_self = min(mhed(nx, ny, rx, ry) for rx, ry in resources if (rx, ry) not in obstacles)
        safe_bias = 0.2 * (opp_best - nearest_self)
        total = cap_bias + center_bias + safe_bias

        if total > best_score:
            best_score = total
            best_move = (dx, dy)

    if best_score == -10**18:
        # All candidate moves blocked; deterministically stay.
        return [0, 0]
    return [best_move[0], best_move[1]]