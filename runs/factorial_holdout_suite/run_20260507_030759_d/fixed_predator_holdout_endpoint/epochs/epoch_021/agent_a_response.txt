def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None  # (primary, secondary, dx, dy)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    valid = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    if not resources:
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy, nx, ny in valid:
            d = abs(nx - tx) + abs(ny - ty)
            if best is None or d < best[0]:
                best = (d, dx, dy)
        return [best[1], best[2]]

    # If late game, prioritize fastest capture; otherwise prioritize denial (keeping opp farther).
    late = observation.get("turns_remaining", 0) <= 4 + len(resources) // 2
    my_move = None
    for dx, dy, nx, ny in valid:
        # Evaluate this move against the best resource to deny.
        best_adv = None
        best_my = None
        best_opp = None
        for rx, ry in resources:
            my_d = abs(nx - rx) + abs(ny - ry)
            opp_d = abs(ox - rx) + abs(oy - ry)
            adv = opp_d - my_d  # higher is better: I move closer than opponent
            if best_adv is None or adv > best_adv or (adv == best_adv and my_d < best_my):
                best_adv = adv
                best_my = my_d
                best_opp = opp_d

        # Primary: denial (or fastest capture if late), Secondary: tie-break by my distance.
        if late:
            primary = best_my
            secondary = -best_opp
            cand = (primary, secondary, dx, dy)
        else:
            primary = -best_adv
            secondary = best_my
            cand = (primary, secondary, dx, dy)

        if my_move is None or cand < my_move:
            my_move = cand

    return [my_move[2], my_move[3]]