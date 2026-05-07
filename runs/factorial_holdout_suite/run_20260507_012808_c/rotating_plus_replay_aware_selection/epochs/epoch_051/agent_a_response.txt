def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def steps(x, y, rx, ry):
        return max(abs(rx - x), abs(ry - y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        return [dx, dy] if valid(nx, ny) else [0, 0]

    best_move = [0, 0]
    best_val = -10**18
    res_list = [tuple(r) for r in resources]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        max_lead = -10**18
        min_ds_for_max_lead = 10**9
        for rx, ry in res_list:
            if (rx, ry) in obstacles:
                continue
            ds = steps(nx, ny, rx, ry)
            do = steps(ox, oy, rx, ry)
            lead = do - ds
            if lead > max_lead:
                max_lead = lead
                min_ds_for_max_lead = ds
            elif lead == max_lead and ds < min_ds_for_max_lead:
                min_ds_for_max_lead = ds

        # Encourage winning resources (positive lead). If none, still minimize our distance and avoid giving opponent tempo.
        nearest_d = min(steps(nx, ny, rx, ry) for rx, ry in res_list if (rx, ry) not in obstacles)
        value = (1000 * max_lead) - nearest_d + (2 if max_lead > 0 else 0) - (0.01 * min_ds_for_max_lead)
        if value > best_val:
            best_val = value
            best_move = [dx, dy]

    return best_move