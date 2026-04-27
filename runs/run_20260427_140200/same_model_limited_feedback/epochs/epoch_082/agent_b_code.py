def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def clamp(x, y):
        if x < 0: x = 0
        elif x >= w: x = w - 1
        if y < 0: y = 0
        elif y >= h: y = h - 1
        return x, y

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = None
    best_val = None

    has_res = len(resources) > 0
    for dx, dy in deltas:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) in obstacles:
            nx, ny = sx, sy
        if (nx, ny) == (ox, oy):
            continue

        if has_res:
            d_self = min(dist((nx, ny), r) for r in resources)
            d_opp_to = min(dist((ox, oy), r) for r in resources)
            # Estimate "contested progress": prioritize moves that reduce own distance,
            # and slightly prefer states where opponent is relatively farther.
            val = (-d_self) + 0.05 * d_opp_to
        else:
            # No resources seen: drift toward center to avoid being trapped.
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            d_center = abs(nx - cx) + abs(ny - cy)
            val = -d_center

        # Deterministic tie-break: lexicographically smallest delta among equals
        if best_val is None or val > best_val or (val == best_val and (dx, dy) < best):
            best_val = val
            best = (dx, dy)

    return [best[0], best[1]]