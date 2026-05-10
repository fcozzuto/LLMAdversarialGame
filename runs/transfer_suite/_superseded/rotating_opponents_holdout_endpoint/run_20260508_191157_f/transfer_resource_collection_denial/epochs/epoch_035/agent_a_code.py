def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    w, h = observation["grid_width"], observation["grid_height"]

    if not resources:
        return [0, 0]

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Pick a target: first favor resources where we are not behind (self_d <= opp_d),
    # then nearest by our distance; deterministic tie-break by coordinates.
    best_t = None
    best_key = None
    for rx, ry in resources:
        sd = abs(rx - sx) + abs(ry - sy)
        od = abs(rx - ox) + abs(ry - oy)
        key = (1 if sd > od else 0, sd, od, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                sd = abs(tx - nx) + abs(ty - ny)
                od = abs(tx - ox) + abs(ty - oy)
                # Higher (sd - od) means worse; we minimize it.
                # Also prefer reducing our distance to the target.
                adv = sd - od
                # Small preference to move closer to target than stay when tied.
                stay_pen = 0 if (dx == 0 and dy == 0) else -0.01
                moves.append(((adv, sd, nx, ny), [dx, dy], stay_pen))

    if not moves:
        return [0, 0]

    # Deterministic: sort by score tuple, then by move vector.
    moves.sort(key=lambda x: (x[0][0] + x[2], x[0][1], x[0][2], x[0][3], x[1][0], x[1][1]))
    return moves[0][1]