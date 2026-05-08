def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        return [dx, dy]

    best = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Counter "sweep_rows": prefer resources far in y from opponent row
        adv = (od - sd) * 10 + abs(ry - oy) - sd * 0.1
        cand = (adv, -sd, -abs(rx - sx), rx, ry)
        if best is None or cand > best:
            best = cand
    rx, ry = best[3], best[4]

    if sx == rx and sy == ry:
        return [0, 0]

    # Local obstacle-aware step selection among all 9 deltas.
    best_step = None
    # Deterministic preference order: stay, then E/W, then N/S, then diagonals in a fixed pattern.
    for dx in (0, 1, -1):
        for dy in (0, 1, -1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            # prioritize immediate reduction to target, then keep opponent farther
            self_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            step = (-(self_d), -(abs((rx - nx)) + abs((ry - ny))), opp_d, dx, dy)
            if best_step is None or step > best_step:
                best_step = step
    if best_step is None:
        return [0, 0]
    return [best_step[3], best_step[4]]