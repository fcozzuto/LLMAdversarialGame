def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    blocked = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    viable = []
    for r in resources:
        rx, ry = r[0], r[1]
        if (rx, ry) not in blocked:
            viable.append((rx, ry))

    if viable:
        best = None
        best_key = None
        for rx, ry in viable:
            myd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            gap = od - myd  # bigger => I am closer / contesting
            key = (-gap, myd, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best
        best_move = None
        best_move_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in blocked:
                dt = cheb(nx, ny, tx, ty)
                do = cheb(nx, ny, ox, oy)
                key = (dt, -do, dx, dy)
                if best_move_key is None or key < best_move_key:
                    best_move_key = key
                    best_move = [dx, dy]
        if best_move is not None:
            return best_move
        return [0, 0]

    # No viable resources: move to the corner farthest from opponent while staying deterministic.
    tx = 0 if (ox + sx) <= (w - 1) else (w - 1)
    ty = 0 if (oy + sy) <= (h - 1) else (h - 1)

    best_move = [0, 0]
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in blocked:
            dt = cheb(nx, ny, tx, ty)
            do = cheb(nx, ny, ox, oy)
            key = (dt, -do, dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best_move = [dx, dy]
    return best_move