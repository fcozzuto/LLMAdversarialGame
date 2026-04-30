def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    resources = [tuple(p) for p in observation["resources"]]
    if not resources:
        return [0, 0]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    # Pick target resource with best advantage (deterministic)
    best_r = None
    best_adv = -10**9
    # Tie-break by distance to self then lexicographic
    for r in resources:
        d1 = dist((sx, sy), r)
        d2 = dist((ox, oy), r)
        adv = d2 - d1
        if adv > best_adv or (adv == best_adv and (d1 < dist((sx, sy), best_r) if best_r else True)) or \
           (adv == best_adv and dist((sx, sy), r) == dist((sx, sy), best_r) if best_r else False and r < best_r):
            best_adv = adv
            best_r = r
    tx, ty = best_r

    # Score each legal move
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        my_d = dist((nx, ny), (tx, ty))
        cur_d = dist((sx, sy), (tx, ty))
        opp_to = dist((ox, oy), (tx, ty))
        new_adv = opp_to - my_d

        # Prefer approaching target; avoid getting too close to opponent
        opp_dist_after = dist((nx, ny), (ox, oy))
        opp_pen = 0
        if opp_dist_after <= 1:
            opp_pen = 20
        elif opp_dist_after == 2:
            opp_pen = 6

        # If landing on any resource, slightly boost (deterministic)
        res_bonus = 0
        if (nx, ny) in set(resources):
            res_bonus = 50

        # Small preference to reduce distance to opponent when we are already ahead,
        # otherwise keep distance (deterministic policy shift)
        ahead = (dist((sx, sy), (tx, ty)) < dist((ox, oy), (tx, ty)))
        opp_move_pref = 0
        if ahead:
            opp_move_pref = -dist((nx, ny), (ox, oy)) * 0.2
        else:
            opp_move_pref = dist((nx, ny), (ox, oy)) * 0.05

        score = (new_adv * 10) + (cur_d - my_d) * 8 + res_bonus - opp_pen + opp_move_pref
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            # deterministic tie-break: smaller dx^2+dy^2 then lexicographic
            if dx * dx + dy * dy < best_move[0] * best_move[0] + best_move[1] * best_move[1]:
                best_move = (dx, dy)
            elif dx * dx + dy * dy == best_move[0] * best_move[0] + best_move[1] * best_move[1] and (dx, dy) < best_move:
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]