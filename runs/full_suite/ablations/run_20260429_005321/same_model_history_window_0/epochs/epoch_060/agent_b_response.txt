def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    INF = 10**9

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def eval_resource(rx, ry):
        d1 = dist((sx, sy), (rx, ry))
        d2 = dist((ox, oy), (rx, ry))
        score = (d2 - d1) * 10 - d1
        # Slight bias to resources not near obstacles
        near_obs = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                if (rx + dx, ry + dy) in obstacles:
                    near_obs += 1
        score -= near_obs * 2
        return score

    if resources:
        best = None
        best_score = -INF
        for rx, ry in resources:
            sc = eval_resource(rx, ry)
            if sc > best_score:
                best_score = sc
                best = (rx, ry)
        tx, ty = best
    else:
        tx, ty = w // 2, h // 2

    best_move = [0, 0]
    best_val = -INF
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h):
                continue
            if (nx, ny) in obstacles:
                continue
            d_self = dist((nx, ny), (tx, ty))
            d_opp = dist((nx, ny), (ox, oy))
            # Primary: get closer to target; Secondary: keep away from opponent; Tertiary: prefer reducing target distance
            val = -d_self * 5 + d_opp * 1
            # Small deterministic preference to moving (avoid staying when equal)
            if dx != 0 or dy != 0:
                val += 0.5
            if val > best_val:
                best_val = val
                best_move = [dx, dy]
    return best_move