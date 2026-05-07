def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    best = None
    best_val = -10**18
    # Evaluate each move by best achievable advantage over any resource this turn.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        move_best = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            # Large weight on stealing/denying race; small penalty for distance.
            adv = od - sd  # positive => we are closer than opponent to that resource
            val = adv * 100 - sd
            # If we are already effectively tied/behind, prefer moves that reduce our distance a lot.
            if adv <= 0:
                val += (0 - adv) * -5  # mild further penalty when behind
                val += -sd // 2
            if val > move_best:
                move_best = val
        # Tie-break: prefer smaller self distance to the single best resource.
        if move_best > best_val:
            best_val = move_best
            best = (dx, dy)
        elif move_best == best_val:
            # compute exact tie-break metrics
            cur_sd_best = 10**18
            cand_sd_best = 10**18
            # for current best
            bdx, bdy = best
            bx, by = sx + bdx, sy + bdy
            for rx, ry in resources:
                if (rx, ry) in obstacles:
                    continue
                sd_b = man(bx, by, rx, ry)
                if sd_b < cur_sd_best:
                    cur_sd_best = sd_b
                sd_c = man(sx + dx, sy + dy, rx, ry)
                if sd_c < cand_sd_best:
                    cand_sd_best = sd_c
            if cand_sd_best < cur_sd_best or (cand_sd_best == cur_sd_best and (dx, dy) < best):
                best = (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]