def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res.append((r[0], r[1]))

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_key = None

    if res:
        for dx, dy in moves:
            nx = clamp(sx + dx, 0, w - 1)
            ny = clamp(sy + dy, 0, h - 1)
            if (nx, ny) in obs:
                continue
            # pick move that maximizes my time advantage to the best target
            my_best = None
            op_best = None
            for rx, ry in res:
                my_t = cheb(nx, ny, rx, ry)
                op_t = cheb(ox, oy, rx, ry)
                if my_best is None or my_t < my_best:
                    my_best = my_t
                if op_best is None or op_t < op_best:
                    op_best = op_t
            adv = (op_best - my_best) if (my_best is not None and op_best is not None) else -10**9
            # tie-breaker: closer to nearest resource after move
            near = my_best if my_best is not None else 10**9
            key = (-adv, near, dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best_move = (dx, dy)
    else:
        tx, ty = w // 2, h // 2
        for dx, dy in moves:
            nx = clamp(sx + dx, 0, w - 1)
            ny = clamp(sy + dy, 0, h - 1)
            if (nx, ny) in obs:
                continue
            d = cheb(nx, ny, tx, ty)
            key = (d, dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]