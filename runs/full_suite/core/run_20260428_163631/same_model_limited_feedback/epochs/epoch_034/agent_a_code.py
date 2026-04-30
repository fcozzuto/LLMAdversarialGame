def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation["obstacles"])
    resources = [(x, y) for x, y in observation["resources"]]
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = None
    best_val = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        if not resources:
            val = -(dist((nx, ny), (ox, oy)))
        else:
            # Choose best target resource, with bias if we can get it sooner than opponent
            val = -10**9
            for rx, ry in resources:
                myd = dist((nx, ny), (rx, ry))
                opd = dist((ox, oy), (rx, ry))
                block_bias = 2.0 if myd <= opd else 0.0
                target_val = (20.0 / (1.0 + myd)) + block_bias - (0.25 * myd) - (0.05 * opd)
                if target_val > val:
                    val = target_val
            # Small preference for reducing our distance to the closest resource overall
            closest_d = min(dist((nx, ny), r) for r in resources)
            val -= 0.02 * closest_d
        if val > best_val:
            best_val = val
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best