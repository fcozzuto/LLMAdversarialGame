def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = {(p[0], p[1]) for p in obstacles}
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_resource_for(pos):
        if not resources:
            return None
        best = None
        best_key = None
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            d = cheb(pos, (rx, ry))
            key = (d, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        return best

    my_best = best_resource_for((sx, sy))
    op_best = best_resource_for((ox, oy))

    center = (w // 2, h // 2)
    if my_best is None and op_best is None:
        tx, ty = center
    else:
        if my_best is None:
            tx, ty = op_best
        elif op_best is None:
            tx, ty = my_best
        else:
            myd = cheb((sx, sy), my_best)
            opd = cheb((ox, oy), my_best)
            # If I'm not competitive, target opponent's closest resource to contest
            if cheb((sx, sy), my_best) > cheb((ox, oy), my_best):
                tx, ty = op_best
            else:
                tx, ty = my_best

    def score_move(nx, ny):
        # Prefer: reach target quickly, avoid giving opponent easy access, avoid staying near obstacles if tie.
        d_my = cheb((nx, ny), (tx, ty))
        d_op = cheb((ox, oy), (tx, ty))
        # If my lead is already good, prioritize shortest arrival; otherwise maximize my advantage after move.
        lead_after = d_op - d_my
        # Small obstacle proximity penalty (deterministic)
        prox = 0
        for ex, ey in obs:
            ddx = nx - ex
            if ddx < 0: ddx = -ddx
            ddy = ny - ey
            if ddy < 0: ddy = -ddy
            dd = ddx if ddx > ddy else ddy
            if dd <= 1:
                prox += 1
        # Tie-breakers: prefer moving toward center slightly to reduce dead-ends
        d_cent = cheb((nx, ny), center)
        return (lead_after, -d_my, -(8 - d_cent), -prox)

    best_mv = (0, 0)
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        key = score_move(nx, ny)
        if best_key is None or key > best_key:
            best_key = key
            best_mv = (dx, dy)

    return [best_mv[0], best_mv[1]]