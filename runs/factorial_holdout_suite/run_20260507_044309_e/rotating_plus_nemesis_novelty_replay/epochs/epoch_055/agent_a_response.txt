def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    res = observation.get("resources") or []
    if not res:
        return [0, 0]
    obstacles_raw = observation.get("obstacles") or []
    obstacles = obstacles_raw if isinstance(obstacles_raw, set) else set(tuple(p) for p in obstacles_raw)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        my_best = 10**9
        op_best = 10**9
        my2_best = 10**9
        op2_best = 10**9

        for rx, ry in res:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            if ds < my_best:
                my2_best, my_best = my_best, ds
            elif ds < my2_best:
                my2_best = ds
            if do < op_best:
                op2_best, op_best = op_best, do
            elif do < op2_best:
                op2_best = do

        # Prefer increasing relative advantage, and also bias toward stealing turn opportunities:
        # - larger (op_best - my_best)
        # - if tie, prefer smaller my_best
        # - if still tie, prefer larger (op2_best - my2_best) to keep a second-option plan
        adv1 = op_best - my_best
        adv2 = op2_best - my2_best
        key = (adv1, adv2, -my_best, -my2_best, -(abs(nx - ox) + abs(ny - oy)), -nx, -ny)
        if best is None or key > best[0]:
            best = (key, [dx, dy])

    return best[1] if best is not None else [0, 0]