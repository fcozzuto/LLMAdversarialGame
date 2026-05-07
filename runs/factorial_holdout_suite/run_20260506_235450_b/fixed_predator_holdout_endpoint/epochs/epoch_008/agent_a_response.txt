def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    tr = observation.get("turns_remaining", 0)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    if not resources:
        tx, ty = (0, h - 1) if (sx + sy) <= (ox + oy) else (w - 1, 0)
    else:
        # Race heuristic: try to pick resources where we are (or can become) faster than opponent.
        # Switch intent when late: greedily collect closest to finish.
        late = (tr <= 6)
        best_t = None
        best_k = None
        for rx, ry in resources:
            sd = man(sx, sy, rx, ry)
            od = man(ox, oy, rx, ry)
            if late:
                k = (-sd, -od, rx, ry)
            else:
                # Prefer positive gap; also avoid resources that are extremely close to opponent.
                gap = od - sd
                k = (gap, -od, -sd, rx, ry)
            if best_k is None or k > best_k:
                best_k = k
                best_t = (rx, ry)
        tx, ty = best_t

    # Move one step toward target; if that is poor (opponent too close), prioritize separating while still improving.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sd2 = man(nx, ny, tx, ty)
        od2 = man(nx, ny, ox, oy)
        # Primary: get closer to target; Secondary: deny by increasing opponent distance if race is unfavorable.
        target_score = -sd2
        sep_bonus = 0
        if resources:
            # If opponent is close to the chosen target, emphasize separation more.
            if man(ox, oy, tx, ty) <= 2:
                sep_bonus = od2
            else:
                sep_bonus = -od2 * 0.05
        k = (target_score, sep_bonus, -man(nx, ny, sx, sy), -nx, -ny)
        if best is None or k > best:
            best = k
            bx, by = dx, dy

    return [int(bx), int(by)]