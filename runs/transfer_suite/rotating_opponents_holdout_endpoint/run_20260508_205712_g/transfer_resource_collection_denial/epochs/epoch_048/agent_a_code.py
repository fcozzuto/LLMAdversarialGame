def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    W, H = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs_set = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    if not resources:
        tx, ty = (W - 1) // 2, (H - 1) // 2
    else:
        best = None
        best_val = -10**9
        for rx, ry in resources:
            sd = abs(rx - sx) + abs(ry - sy)
            od = abs(rx - ox) + abs(ry - oy)
            val = (od - sd) * 10 - sd * 0.01  # prefer resources we can reach earlier
            if val > best_val:
                best_val = val
                best = (rx, ry)
        tx, ty = best

    best_move = (0, 0)
    best_score = -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        dist = abs(tx - nx) + abs(ty - ny)
        opp_dist = abs(tx - nx) + abs(ty - ny)  # same dist form; used only for tie consistency
        # Main goal: minimize distance to target, then slightly prefer moving away from opponent when tied.
        score = -dist - 0.001 * (abs(nx - ox) + abs(ny - oy))
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]