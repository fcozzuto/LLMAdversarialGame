def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Pick a target resource: prefer ones I'm closer to than opponent (security).
    best_t = None
    best_gain = None
    for r in resources:
        rx, ry = r
        myd = dist((sx, sy), (rx, ry))
        opd = dist((ox, oy), (rx, ry))
        gain = opd - myd
        if best_t is None or gain > best_gain or (gain == best_gain and myd < dist((sx, sy), best_t)):
            best_t = (rx, ry)
            best_gain = gain
    if best_t is None:
        # No resources visible: drift toward center.
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        tx, ty = best_t

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        my_to_target = dist((nx, ny), (tx, ty))
        opp_to_target = dist((ox, oy), (tx, ty))
        # Score: move closer to target, keep advantage over opponent, avoid opponent proximity.
        opp_prox = abs(nx - ox) + abs(ny - oy)
        score = -my_to_target + 2.0 * (opp_to_target - dist((nx, ny), (tx, ty))) + 0.15 * opp_prox
        if (nx, ny) == (tx, ty):
            score += 50.0
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]