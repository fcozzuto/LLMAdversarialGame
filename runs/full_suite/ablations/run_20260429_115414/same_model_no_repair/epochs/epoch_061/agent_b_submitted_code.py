def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles_list = observation.get("obstacles", [])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    obs = set((p[0], p[1]) for p in obstacles_list)
    if not resources:
        return [0, 0]

    def cd(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

    def mindist_to_obstacles(x, y):
        if not obs:
            return 10
        m = 10
        for ox2, oy2 in obs:
            d = max(abs(x - ox2), abs(y - oy2))
            if d < m:
                m = d
        return m

    # Mode switch to change strategy materially when we're not ahead
    even_mode = (observation.get("turn_index", 0) % 2 == 0)

    # Target selection
    best_t = None
    best_key = None
    for r in resources:
        rx, ry = r[0], r[1]
        d_s = cd((sx, sy), (rx, ry))
        d_o = cd((ox, oy), (rx, ry))
        if even_mode:
            key = (d_o - d_s, -d_s, -rx, -ry)  # maximize our advantage
        else:
            # denial race: prefer resources we're not farther from; otherwise still race closest
            key = ((0 if d_s <= d_o else 1), d_s, d_o, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t

    candidates = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_score = None

    cur_to_t = cd((sx, sy), (tx, ty))
    cur_opp_to_t = cd((ox, oy), (tx, ty))

    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obs:
            continue

        self_d = cd((nx, ny), (tx, ty))
        opp_d = cur_opp_to_t  # opponent doesn't move this turn (relative to our choice)
        advantage = opp_d - self_d

        # Slight preference to progress; and avoid stalling
        progress = cur_to_t - self_d  # positive if closer

        # Obstacle safety: stay away from obstacles (deterministic shaping)
        safety = mindist_to_obstacles(nx, ny) - mindist_to_obstacles(sx, sy)

        # Also discourage drifting in a way that increases distance to target's vicinity
        # by combining Chebyshev and a tiny coordinate bias for tie-breaking
        tie_bias = -abs(nx - tx) - abs(ny - ty) * 0.001

        score = (advantage * 100.0) + (progress * 5.0) + (safety * 1.0) + tie_bias
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best