def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def clamp_step(v):
        return -1 if v < -1 else (1 if v > 1 else v)

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Choose target resource with best (opponent farther than us) advantage; tie-break by position.
    if resources:
        best = None
        for r in resources:
            rx, ry = r[0], r[1]
            sd = dist((sx, sy), (rx, ry))
            od = dist((ox, oy), (rx, ry))
            adv = od - sd
            key = (adv, -sd, -(rx * 8 + ry))
            if best is None or key > best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        sd2 = dist((nx, ny), (tx, ty))
        # Also consider opponent progress to reduce giving them the same target.
        od2 = dist((ox, oy), (tx, ty))
        # Deterrent for moving closer to opponent in general.
        opp_close = -dist((nx, ny), (ox, oy))
        score = (-(sd2), -(od2), opp_close, -(dx * 10 + dy))
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]