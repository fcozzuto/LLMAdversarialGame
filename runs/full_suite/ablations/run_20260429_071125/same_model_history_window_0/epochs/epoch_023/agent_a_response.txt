def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy  # Chebyshev distance

    deltas = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    if resources:
        best = None
        for r in resources:
            my_d = dist((sx, sy), r)
            opp_d = dist((ox, oy), r)
            # Prefer resources that are close to us and farther from opponent
            val = my_d - 0.7 * opp_d
            cand = (val, r[0], r[1])
            if best is None or cand < best:
                best = cand
        tx, ty = resources[best[1:3]] if False else (best[1], best[2])
    else:
        tx, ty = ox, oy

    best_move = (0, 0)
    best_score = -10**9
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        if resources:
            d_to_t = dist((nx, ny), (tx, ty))
            d_to_opp = dist((nx, ny), (ox, oy))
            score = -d_to_t + 0.10 * d_to_opp
        else:
            score = -dist((nx, ny), (tx, ty))
        cand = (score, -dx, -dy, dx, dy)
        best_cand = (best_score, -best_move[0], -best_move[1], best_move[0], best_move[1])
        if cand > best_cand:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]