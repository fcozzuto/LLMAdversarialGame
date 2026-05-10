def choose_move(observation):
    sx, sy = observation["self_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    my_set = {(p[0], p[1]) for p in (observation.get("self_territory") or [])}
    opp_set = {(p[0], p[1]) for p in (observation.get("opponent_territory") or [])}
    un_set = {(p[0], p[1]) for p in (observation.get("unclaimed_cells") or [])}
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if sx < 0 or sy < 0:
        return [0, 0]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    my_near = None
    if my_set:
        bestd = 10**9
        for (x, y) in my_set:
            d = abs(x - sx) + abs(y - sy)
            if d < bestd:
                bestd = d
        my_near = bestd

    opp_near = None
    if opp_set:
        bestd = 10**9
        for (x, y) in opp_set:
            d = abs(x - sx) + abs(y - sy)
            if d < bestd:
                bestd = d
        opp_near = bestd

    best = None
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        score = 0.0

        if (nx, ny) in opp_set:
            score += 6.0
        elif (nx, ny) in un_set:
            score += 3.5
        elif (nx, ny) in my_set:
            score += 1.0
        else:
            score += 0.2

        score += -0.20 * (abs(nx - cx) + abs(ny - cy))

        if my_near is not None:
            score += 0.10 * (my_near - (abs(nx - sx) + abs(ny - sy)))
        if opp_near is not None:
            score += 0.08 * (opp_near - (abs(nx - sx) + abs(ny - sy)))

        # If close to opponent territory, bias toward their frontier to enable flips.
        frontier = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx or ddy:
                    if (nx + ddx, ny + ddy) in opp_set:
                        frontier += 1
        score += 0.9 * frontier

        if best is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]