def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set(obstacles_list) if isinstance(obstacles_list, set) else set(tuple(p) for p in obstacles_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    if not resources:
        return [0, 0]

    best_res = None
    best_key = None
    for rx, ry in resources:
        ds = abs(rx - sx) + abs(ry - sy)
        do = abs(rx - ox) + abs(ry - oy)
        # resource_denier: if opponent is close, prefer resources that are still closer for us
        adv = do - ds  # positive => we are closer
        # slight preference for staying aligned with opponent's y (often their sweep axis)
        key = (-adv, ds, abs(ry - oy), rx, ry)
        # We want minimal key; because -adv, larger adv => smaller key
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry, ds, do, adv)

    tx, ty, ds, do, adv = best_res

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_mkey = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        n_ds = abs(tx - nx) + abs(ty - ny)
        n_do = abs(tx - ox) + abs(ty - oy)  # opponent not moving yet
        # If opponent is threatening (we're not closer), bias to increase their distance while still making progress.
        n_opp_dist = abs(ox - nx) + abs(oy - ny)
        progress = n_ds - ds
        # prefer: reduce distance to target; if tie, prefer being closer than opponent (adv grows);
        # and when contesting, prefer to keep opponent farther.
        mkey = (progress, (n_do - n_ds) * -1, -n_opp_dist, abs(ty - ny) + abs(tx - nx), dx, dy)
        if best_mkey is None or mkey < best_mkey:
            best_mkey = mkey
            best_move = [dx, dy]

    # If all moves invalid (e.g., surrounded by obstacles), stay.
    return best_move if best_move is not None else [0, 0]