def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    resources = observation["resources"]

    if not resources:
        return [0, 0]

    # Choose resource where we are ahead (deterministic tie-break)
    best = None
    best_key = None
    for rx, ry in resources:
        myd = abs(rx - sx) + abs(ry - sy)
        opd = abs(rx - ox) + abs(ry - oy)
        adv = opd - myd  # larger => we are closer
        key = (-adv, myd, opd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # One-step greedy with deterministic tie-break; avoid obstacles/out-of-bounds.
    best_move = (0, 0)
    best_key = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or nx >= w or ny < 0 or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            myd = abs(tx - nx) + abs(ty - ny)
            opd = abs(tx - ox) + abs(ty - oy)
            adv_after = opd - myd
            # Prefer: more advantage, then closer to target, then deterministic preference toward lower (x,y)
            key = (-adv_after, myd, abs(nx - ox) + abs(ny - oy), nx, ny, dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best_move = (dx, dy)

    return [best_move[0], best_move[1]]