def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    if not resources:
        # fallback: move toward opponent if no resources visible
        best = [0, 0]
        bestd = -10**9
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = x + dx, y + dy
                if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                    continue
                d = -( (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy) )
                if d > bestd:
                    bestd = d
                    best = [dx, dy]
        return best

    def dsq(a, b, c, d):
        return (a - c) * (a - c) + (b - d) * (b - d)

    # Choose target resource where we have relative advantage
    best_r = None
    best_val = 10**18
    for rx, ry in resources:
        myd = dsq(x, y, rx, ry)
        opd = dsq(ox, oy, rx, ry)
        val = myd - 0.6 * opd
        if val < best_val:
            best_val = val
            best_r = (rx, ry)
    tx, ty = best_r

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # Primary step: move toward target
    stepx = 0 if tx == x else (1 if tx > x else -1)
    stepy = 0 if ty == y else (1 if ty > y else -1)
    cand_moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = x + dx, y + dy
            if dx == 0 and dy == 0:
                pass
            if legal(nx, ny):
                cand_moves.append((dx, dy, nx, ny))

    # Prefer moves that reduce distance to target, with slight penalty if we give opponent closer access
    cur_my = dsq(x, y, tx, ty)
    cur_opd = dsq(ox, oy, tx, ty)
    best = [0, 0]
    best_score = -10**18
    for dx, dy, nx, ny in cand_moves:
        myd = dsq(nx, ny, tx, ty)
        opd = cur_opd  # opponent doesn't change this turn
        # "trap" effect: if we move onto/near opponent, avoid; but allow if it helps winning target
        opp_near_pen = -0.05 * dsq(nx, ny, ox, oy)
        # score higher is better
        score = (cur_my - myd) * 10.0 - 0.15 * (myd) + opp_near_pen + (opd * -0.01)
        if myd < cur_my or (dx == stepx and dy == stepy):
            score += 0.5
        if score > best_score:
            best_score = score
            best = [dx, dy]
    return best