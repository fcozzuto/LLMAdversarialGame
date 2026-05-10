def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))  # diagonal-allowed

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def best_adv_at(pos):
        best_key = None
        best_res = None
        for rx, ry in resources:
            s_d = dist(pos, (rx, ry))
            o_d = dist((ox, oy), (rx, ry))
            # primary: prefer resources we are closer to than opponent
            # secondary: prefer smaller self distance
            # tertiary: deterministic by coordinates
            key = (-(o_d - s_d), s_d, rx, ry)
            if best_key is None or key < best_key:
                best_key, best_res = key, (rx, ry)
        return best_key, best_res

    best_overall = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        key, _ = best_adv_at((nx, ny))
        if key is None:
            continue
        # Encourage breaking ties by also moving toward opponent-threat (increases contest)
        o_to_self = dist((ox, oy), (nx, ny))
        total = (key[0], key[1], o_to_self, nx, ny)
        if best_overall is None or total < best_overall:
            best_overall = total
            best_move = [dx, dy]

    return best_move