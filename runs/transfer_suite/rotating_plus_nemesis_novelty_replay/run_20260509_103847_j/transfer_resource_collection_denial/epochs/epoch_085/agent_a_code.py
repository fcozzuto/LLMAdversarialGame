def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set(obstacles_list) if isinstance(obstacles_list, set) else set(tuple(p) for p in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    best_move = None
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Evaluate this move by the best "we are closer" advantage it creates.
        # adv = (opponent_dist - our_dist). Higher is better.
        best_adv = -10**9
        best_ds = 10**9
        for rx, ry in resources:
            ds = abs(rx - nx) + abs(ry - ny)
            do = abs(rx - ox) + abs(ry - oy)
            adv = do - ds
            # Prefer resources that align with opponent's row to contest lanes.
            lane = 1 if ry == oy else 0
            # Small bias for not taking too long to reach.
            ds_bias = ds + (0.35 if lane else 0.0)
            if adv > best_adv or (adv == best_adv and ds_bias < best_ds):
                best_adv = adv
                best_ds = ds_bias

        # If we can beat the opponent on some resource (adv>0), maximize that advantage.
        # Otherwise minimize our distance to the best available resource.
        if best_adv > 0:
            val = (-1.0 * best_adv, best_ds, dx, dy)
        else:
            # Try to head toward any resource while also slightly reducing opponent lead.
            # Using best_adv (negative or zero) makes us prefer moves that improve it.
            val = (0.0, -1.0 * best_adv, best_ds, dx, dy)

        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [best_move[0], best_move[1]]