def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        deltas = [[0, 0], [1, 0], [0, 1], [-1, 0], [0, -1], [1, 1], [-1, 1], [1, -1], [-1, -1]]
        best = None
        bestv = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                v = abs(nx - cx) + abs(ny - cy)
                if bestv is None or v < bestv:
                    bestv = v
                    best = [dx, dy]
        return best if best is not None else [0, 0]

    deltas = [[0, 0], [1, 0], [0, 1], [-1, 0], [0, -1], [1, 1], [-1, 1], [1, -1], [-1, -1]]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_move = [0, 0]
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        my_pos = (nx, ny)
        # Pick the most contested resource: minimize (my_dist - opp_dist), then favor smaller my_dist
        best_val = None
        best_my_d = None
        for rx, ry in resources:
            r = (rx, ry)
            my_d = dist(my_pos, r)
            opp_d = dist((ox, oy), r)
            val = my_d - opp_d
            if best_val is None or val < best_val or (val == best_val and my_d < best_my_d):
                best_val = val
                best_my_d = my_d
        score = best_val * 10 + best_my_d
        if best_score is None or score < best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move