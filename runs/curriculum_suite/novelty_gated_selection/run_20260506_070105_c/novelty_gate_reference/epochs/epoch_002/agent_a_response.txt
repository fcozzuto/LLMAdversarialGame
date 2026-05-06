def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = observation["obstacles"]
    blocked = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    # Pick a target resource deterministically with "contested advantage" first.
    if resources:
        best_r = None
        best_key = None
        for rx, ry in resources:
            du = abs(rx - sx) + abs(ry - sy)
            do_ = abs(rx - ox) + abs(ry - oy)
            contested_adv = do_ - du  # positive means we are closer
            # Prefer being meaningfully closer; if tied, prefer larger contested_adv then nearer to us
            key = (-1 if contested_adv > 0 else 1, -contested_adv, du, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best_r = (rx, ry)
        tx, ty = best_r
    else:
        tx, ty = ox, oy

    candidates = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    # Evaluate moves by: distance-to-target reduction, then deny opponent (increase opponent dist),
    # then break ties toward center-ish to avoid getting stuck.
    best_move = [0, 0]
    best_score = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        du_next = abs(nx - tx) + abs(ny - ty)

        if resources:
            # Opponent's closest remaining resource from their next position (use their current move direction implicitly).
            # We'll approximate by their current best distance to any resource.
            do_best = None
            for rx, ry in resources:
                do_ = abs(rx - ox) + abs(ry - oy)
                if do_best is None or do_ < do_best:
                    do_best = do_
            # Deny: make us closer to our target and keep opponent's best distance from shrinking too fast is hard;
            # instead encourage moves that increase our advantage vs opponent at target.
            opp_dist_to_target = abs(ox - tx) + abs(oy - ty)
            advantage = opp_dist_to_target - du_next
        else:
            du_next = abs(nx - tx) + abs(ny - ty)
            do_best = 0
            advantage = -du_next

        cx_bias = -abs((nx - (w - 1) / 2)) - abs((ny - (h - 1) / 2))
        score = (0, )
        # Higher is better; build scalar from components.
        score = (advantage, -du_next, cx_bias, -abs(nx - ox) - abs(ny - oy), -dx, -dy)

        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]