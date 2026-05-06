def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def sign(v):
        return 0 if v == 0 else (1 if v > 0 else -1)

    if not resources:
        return [sign(ox - x), sign(oy - y)]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = [0, 0]
    best_val = None
    best_tb = None

    for dx, dy in dirs:
        nx, ny = x + dx, y + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        # Evaluate best resource we could aim for after this move
        local_best = None
        local_tb = None
        for tx, ty in resources:
            d_me = abs(tx - nx) + abs(ty - ny)
            d_opp = abs(tx - ox) + abs(ty - oy)
            # Prefer being closer than opponent, but also move toward generally valuable cells
            tv = (d_opp - d_me) * 1000 - d_me
            # Tie-break: prefer smaller opponent distance (more contested earlier)
            tb = (d_opp, d_me, tx, ty)
            if local_best is None or tv > local_best or (tv == local_best and tb < local_tb):
                local_best = tv
                local_tb = tb

        # Global tie-break: prefer higher tv, then lower our distance to that resource, then closer to opponent's current target
        if best_val is None or local_best > best_val:
            best_val = local_best
            best_tb = local_tb
            best_move = [dx, dy]
        elif local_best == best_val:
            cand_tb = local_tb
            if cand_tb is not None and (best_tb is None or cand_tb < best_tb):
                best_tb = cand_tb
                best_move = [dx, dy]

    return best_move if best_move != [0, 0] else [sign(ox - x), sign(oy - y)]