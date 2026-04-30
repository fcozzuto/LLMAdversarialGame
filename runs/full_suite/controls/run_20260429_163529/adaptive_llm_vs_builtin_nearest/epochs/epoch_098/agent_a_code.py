def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        best = (10**9, -1, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny) or (nx, ny) in obstacles:
                continue
            d_opp = cheb(nx, ny, ox, oy)
            if (d_opp, -abs(dx), -abs(dy)) > (best[1], best[2], best[3]):
                best = (best[0], d_opp, -abs(dx), -abs(dy))
        return [int(best[2] and -best[2] or 0), int(best[3] and -best[3] or 0)] if best[1] >= 0 else [0, 0]

    # Pick a resource where we are relatively closer than the opponent.
    best_r = None
    best_key = (10**9, -1, 0, 0)
    for rx, ry in resources:
        my = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        key = (my - opd, -opd, my, rx, ry)
        if key < best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r
    best_move = (10**9, -10**9, 0, 0)  # (dist_to_target, -dist_to_opp, -progress, tie)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obstacles:
            continue
        d_t = cheb(nx, ny, tx, ty)
        d_o = cheb(nx, ny, ox, oy)
        my_before = cheb(sx, sy, tx, ty)
        progress = my_before - d_t  # positive means closer
        tie = (dx, dy)
        key = (d_t, -d_o, -progress, tie)
        if key < best_move:
            best_move = key

    dx, dy = best_move[3][0], best_move[3][1]
    return [int(dx), int(dy)]