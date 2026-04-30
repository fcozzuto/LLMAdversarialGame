def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation["obstacles"]
    resources = observation["resources"]

    obstacle_set = set((p[0], p[1]) for p in obstacles)

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev for 8-dir moves

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # If resources exist: race them with preference for ones opponent reaches later.
    if resources:
        best_move = (0, 0)
        best_score = -10**9
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacle_set:
                nx, ny = sx, sy
            if (nx, ny) in set((p[0], p[1]) for p in resources):
                return [dx, dy]
            my_best = 10**9
            margin_best = -10**9
            for rx, ry in resources:
                my_d = dist((nx, ny), (rx, ry))
                op_d = dist((ox, oy), (rx, ry))
                margin = op_d - my_d
                if margin > margin_best or (margin == margin_best and my_d < my_best):
                    margin_best = margin
                    my_best = my_d
            score = margin_best * 100 - my_best  # prioritize winning race; then closer
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # No resources: drift toward center while not stepping into obstacles.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacle_set:
            nx, ny = sx, sy
        # higher is better: negative distance to center, slight preference away from opponent
        center_d = abs(nx - cx) + abs(ny - cy)
        opp_d = dist((nx, ny), (ox, oy))
        score = -center_d + 0.05 * opp_d
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]