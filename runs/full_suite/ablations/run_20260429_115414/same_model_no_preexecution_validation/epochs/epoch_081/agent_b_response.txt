def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [w - 1, h - 1]) or [w - 1, h - 1]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    best_move = (0, 0)
    best_val = -10**9

    if not resources:
        tx, ty = (w - 1, h - 1) if cheb(sx, sy, w - 1, h - 1) <= cheb(sx, sy, 0, 0) else (0, 0)
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not inside(nx, ny):
            continue
        cur = -cheb(nx, ny, ox, oy) * 0.02  # tiny preference to not get too close
        for rx, ry in resources:
            my_t = cheb(nx, ny, rx, ry)
            op_t = cheb(ox, oy, rx, ry)
            # Prefer resources I can reach no later than opponent; otherwise deprioritize.
            val = (op_t - my_t) - 1.1 * my_t * 0.05
            if op_t <= my_t:
                val += 0.8
            cur += val * 0.12  # aggregate across nearby prospects deterministically
        if cur > best_val:
            best_val = cur
            best_move = (mx, my)

    return [int(best_move[0]), int(best_move[1])]