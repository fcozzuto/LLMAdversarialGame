def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                resources.append((rx, ry))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Choose targets biased toward resources we are more likely to reach first, with a corner-to-corner pressure.
    best_t = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # prefer if we can beat opponent; otherwise still allow, but penalize
        win_bias = do - ds  # positive => we are closer
        side_bias = cheb(rx, ry, 0, 0) - cheb(rx, ry, w - 1, h - 1)
        key = (-win_bias, ds, -side_bias, rx, ry) if win_bias >= 0 else (0, ds + 2, side_bias, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    # If no visible resources, go to a strategic mid-spiral toward opponent's side while avoiding obstacles.
    if best_t is None:
        tx, ty = (w - 1 + sx) // 2, (h - 1 + sy) // 2
    else:
        tx, ty = best_t

    # Local evaluation for next move: progress to target, plus obstacle-aware repulsion near blocked tiles.
    def repulsion(nx, ny):
        p = 0
        for bx, by in blocked:
            d = cheb(nx, ny, bx, by)
            if d == 0:
                return 999
            if d == 1:
                p += 3
        return p

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            continue

        d_now = cheb(sx, sy, tx, ty)
        d_next = cheb(nx, ny, tx, ty)
        target_progress = d_now - d_next  # higher is better
        rpen = repulsion(nx, ny)

        # Contest pressure: don't drift closer to a target if opponent is already much closer.
        if resources:
            # estimate closest competition direction cheaply by using current target and opponent distance
            do_next = cheb(ox, oy, tx, ty)
            opp_bias = (do_next - d_next)  # if positive, we are closer than opponent to the same target
        else:
            opp_bias = 0

        val = (-rpen, -target_progress, -opp_bias, nx, ny)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]