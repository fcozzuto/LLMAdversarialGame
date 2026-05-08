def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obs:
                continue
            d = abs(nx - tx) + abs(ny - ty)
            v = -d + 0.1 * (abs(nx - ox) + abs(ny - oy))
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        my_dist0 = abs(nx - ox) + abs(ny - oy)
        my_best = -10**18
        for rx, ry in resources:
            my_d = abs(nx - rx) + abs(ny - ry)
            opp_d = abs(ox - rx) + abs(oy - ry)
            margin = opp_d - my_d  # positive means I reach first
            value = 14 * margin - my_d
            value += 0.2 * (abs(nx - rx) + abs(ny - ry) == 0)  # slight preference for landing
            value += -0.05 * my_dist0  # prefer staying away a bit from opponent
            if value > my_best:
                my_best = value
        if my_best > best_val or (my_best == best_val and (dx, dy) < best_move):
            best_val = my_best
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]