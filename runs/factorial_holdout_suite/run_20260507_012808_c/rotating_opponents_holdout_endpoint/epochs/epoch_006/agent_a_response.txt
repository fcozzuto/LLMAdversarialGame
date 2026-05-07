def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # If no resources, move toward center-ish.
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = [0, 0]
        bestv = -10**9
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if nx < 0 or ny < 0 or nx >= w or ny >= h: 
                    continue
                if (nx, ny) in obstacles: 
                    continue
                v = -cheb(nx, ny, tx, ty)
                if v > bestv:
                    bestv = v; best = [dx, dy]
        return best

    # Choose a target resource to maximize (opponent distance - our distance).
    # If we can't be closer to any, pick the one with smallest deficit.
    best_r = None
    best_adv = -10**9
    best_ds = 10**9
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds
        if adv > best_adv or (adv == best_adv and ds < best_ds):
            best_adv = adv; best_ds = ds; best_r = (rx, ry)

    rx, ry = best_r
    my_lead = best_adv >= 0

    # Evaluate one-step moves with obstacle and bounds; deterministic tie-breaking.
    best_move = [0, 0]
    best_val = -10**18
    # Fixed order for determinism
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if nx < 0 or ny < 0 or nx >= w or ny >= h:
                continue
            if (nx, ny) in obstacles:
                continue
            ds2 = cheb(nx, ny, rx, ry)
            # If contested (we are behind), nudge toward opponent to "shadow" / contest.
            block_bonus = 0
            if not my_lead:
                block_bonus = -0.05 * cheb(nx, ny, ox, oy)
            # Primary: reduce distance to target; secondary: deterministic prefer moves that also reduce our distance to opponent slightly when behind.
            val = -ds2 + block_bonus
            if val > best_val or (val == best_val and [dx, dy] < best_move):
                best_val = val
                best_move = [dx, dy]
    return best_move