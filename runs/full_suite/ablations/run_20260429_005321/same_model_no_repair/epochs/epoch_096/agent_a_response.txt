def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        ay = y1 - y2
        if ay < 0: ay = -ay
        return ax if ax > ay else ay

    adj8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    adj4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def danger(x, y):
        if (x, y) in obst:
            return 10**6
        d = 0
        for ddx, ddy in adj4:
            if (x + ddx, y + ddy) in obst:
                d += 3
        for ddx, ddy in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            if (x + ddx, y + ddy) in obst:
                d += 1
        return d

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if resources and any((sx, sy) == (rx, ry) for rx, ry in resources):
        return [0, 0]

    best_move = (0, 0, sx, sy)
    best_val = -10**18

    # If resources exist, move to maximize our distance advantage over opponent for the best resource.
    # If no resources, minimize our distance to opponent (safer to control).
    if resources:
        for dx, dy, nx, ny in legal:
            dv = -10**18
            for rx, ry in resources:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                # Prefer positions where we are closer than opponent; also break ties by smaller myd.
                score = (opd - myd) * 10 - myd
                if score > dv:
                    dv = score
            val = dv - danger(nx, ny)
            # Mild bias toward moving (avoid getting stuck on edges if equal)
            dist_from_start = cheb(nx, ny, sx, sy)
            val -= dist_from_start * 0.01
            if val > best_val:
                best_val = val
                best_move = (dx, dy, nx, ny)
    else:
        for dx, dy, nx, ny in legal:
            my_to_opp = cheb(nx, ny, ox, oy)
            opp_to_me = cheb(ox, oy, sx, sy)
            val = (opp_to_me - my_to_opp) * 10 - danger(nx, ny)
            if val > best_val:
                best_val = val
                best_move = (dx, dy, nx, ny)

    return [best_move[0], best_move[1]]