def choose_move(observation):
    self_pos = observation["self_position"]
    opp_pos = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    resources = observation.get("resources", [])
    W = observation["grid_width"]
    H = observation["grid_height"]

    ox = {p[0] for p in obstacles}
    oy = {p[1] for p in obstacles}
    obs_set = {(p[0], p[1]) for p in obstacles}

    sx, sy = int(self_pos[0]), int(self_pos[1])
    tx_opp, ty_opp = int(opp_pos[0]), int(opp_pos[1])

    # If no resources, drift toward center while avoiding obstacles
    if not resources:
        cx, cy = (W - 1) // 2, (H - 1) // 2
        tx, ty = cx, cy
    else:
        best = None
        # Deterministic order: sort by x,y
        for rx, ry in sorted(resources):
            rx, ry = int(rx), int(ry)
            if (rx, ry) in obs_set:
                continue
            my_d = max(abs(rx - sx), abs(ry - sy))
            opp_d = max(abs(rx - tx_opp), abs(ry - ty_opp))
            # Prefer resources where we have advantage; break ties by closer distance then by coords
            adv = opp_d - my_d
            cand = (adv, -my_d, -rx, -ry)
            if best is None or cand > best[0]:
                best = (cand, rx, ry)
        tx, ty = best[1], best[2]

    dx_t = 0 if tx == sx else (1 if tx > sx else -1)
    dy_t = 0 if ty == sy else (1 if ty > sy else -1)
    desired = (dx_t, dy_t)

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    # Prefer desired direction first, then others by distance to target, then deterministic tie-break
    ranked = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= W or ny < 0 or ny >= H:
            continue
        if (nx, ny) in obs_set:
            continue
        d = max(abs(tx - nx), abs(ty - ny))
        pref = 1 if (dx, dy) == desired else 0
        ranked.append((pref, -d, -nx, -ny, dx, dy))
    if not ranked:
        return [0, 0]
    ranked.sort(reverse=True)
    return [int(ranked[0][4]), int(ranked[0][5])]