def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    best_cell = (sx, sy)
    best_key = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        best_adv = None
        best_ds = None
        best_do = None

        for rx, ry in resources:
            my_d = man(nx, ny, rx, ry)
            opp_d = man(ox, oy, rx, ry)
            adv = opp_d - my_d
            if best_adv is None or (adv, -my_d, -opp_d, rx, ry) > (best_adv, -best_ds, -best_do, best_cell[0], best_cell[1]):
                best_adv = adv
                best_ds = my_d
                best_do = opp_d

        opp_pressure = man(nx, ny, ox, oy)
        # Prefer higher advantage; break ties by closer-to-best resource and farther-from-opponent.
        key = (best_adv, -best_ds, -opp_pressure, nx, ny)
        if best_key is None or key > best_key:
            best_key = key
            best_cell = (nx, ny)

    return [best_cell[0] - sx, best_cell[1] - sy]