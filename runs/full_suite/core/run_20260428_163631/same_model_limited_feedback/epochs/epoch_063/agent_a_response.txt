def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    my_pos = (sx, sy)
    opp_pos = (ox, oy)
    if not resources:
        target = opp_pos
    else:
        best = None
        best_val = -10**9
        for rx, ry in resources:
            rd = dist(my_pos, (rx, ry))
            od = dist(opp_pos, (rx, ry))
            # prefer resources where we are not behind; if behind, still choose ones with large lead potential
            val = (od - rd) * 3 - rd
            # slight preference for nearer overall when values tie
            val -= 0.1 * (abs(rx - (w - 1)/2) + abs(ry - (h - 1)/2))
            if val > best_val:
                best_val = val
                best = (rx, ry)
        target = best

    # If opponent is adjacent to our target, switch to a local blocking/intercept: move to maximize distance to target for opponent
    if resources:
        td = dist(opp_pos, target)
        if td <= 2:
            # choose a point near target that is closer to us than to opponent
            best_blk = target
            best_blk_val = -10**9
            tx, ty = target
            for px in (tx-1, tx, tx+1):
                for py in (ty-1, ty, ty+1):
                    if 0 <= px < w and 0 <= py < h and (px, py) not in obstacles:
                        v = (dist((sx, sy), (px, py)) * -1) + (dist(opp_pos, (px, py))) * 1
                        if v > best_blk_val:
                            best_blk_val = v
                            best_blk = (px, py)
            target = best_blk

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy, nx, ny in candidates:
        my_d = dist((nx, ny), target)
        opp_d = dist((nx, ny), opp_pos)
        to_opp_target = dist(opp_pos, target)
        # if we are on a resource, strongly prefer staying/taking it
        res_here = 1 if any(rx == nx and ry == ny for rx, ry in resources) else 0
        # discourage moves that give opponent an immediate claim: after move, compare who is closer to target
        my_after = my_d
        opp_after = to_opp_target  # opponent position unchanged during our move
        contest = (opp_after - my_after)
        score = 0
        score += res_here * 1000
        score += contest * 12
        score += -my_d * 3
        score += opp_d * 0.5
        # mild bias away from edges to reduce trapping
        score += -0.02 * (abs(nx - (w - 1)/2) + abs(ny - (h - 1)/2))
        # small bias toward not moving diagonally unless it helps (deterministic tie-break)
        score += -(0.01 if dx != 0 and dy != 0 else 0)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]