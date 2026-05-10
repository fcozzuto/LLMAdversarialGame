def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    W, H = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs_set = {(p[0], p[1]) for p in obstacles}

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    if not resources:
        tx, ty = (0 if ox > sx else W - 1), (0 if oy > sy else H - 1)
    else:
        best = None
        best_key = None
        for rx, ry in resources:
            sd = abs(rx - sx) + abs(ry - sy)
            od = abs(rx - ox) + abs(ry - oy)
            # Prefer resources we can reach sooner; if tied/late, prefer far-from-opponent-after-arrival.
            key = (od - sd, -(sd), -(abs(rx - (W - 1 - sx)) + abs(ry - (H - 1 - sy))))
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best

    # If opponent is significantly closer to the best resource, drift slightly toward a runner-up to avoid being "shadowed"
    if resources:
        myd_best = abs(tx - sx) + abs(ty - sy)
        opd_best = abs(tx - ox) + abs(ty - oy)
        if opd_best - myd_best >= 2:
            best2, best2_key = (tx, ty), (-10**9, 10**9)
            for rx, ry in resources:
                sd = abs(rx - sx) + abs(ry - sy)
                od = abs(rx - ox) + abs(ry - oy)
                key = (od - sd, sd)
                if key[0] > best2_key[0] or (key[0] == best2_key[0] and key[1] < best2_key[1]):
                    best2_key = key
                    best2 = (rx, ry)
            tx, ty = best2

    # Choose the step that minimizes our distance to target, with tie-break favoring keeping opponent farther from target.
    best_move = (0, 0)
    best_tuple = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        my_dist = abs(tx - nx) + abs(ty - ny)
        op_dist = abs(tx - ox) + abs(ty - oy)
        # Favor progress; discourage moving into states that make us lose the race further.
        t = (my_dist, -(op_dist - my_dist), abs(nx - ox) + abs(ny - oy))
        if best_tuple is None or t < best_tuple:
            best_tuple = t
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]