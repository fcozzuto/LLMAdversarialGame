def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    blocked = set((p[0], p[1]) for p in obstacles)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def sgn(v): return 0 if v == 0 else (1 if v > 0 else -1)

    viable = [(r[0], r[1]) for r in resources if (r[0], r[1]) not in blocked]
    if not viable:
        tx = w - 1 if (sx + ox) < w - 1 else 0
        ty = h - 1 if (sy + oy) < h - 1 else 0
        return [sgn(tx - sx), sgn(ty - sy)]

    best = None
    best_key = None
    for rx, ry in viable:
        myd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        contest = od - myd  # positive => we reach earlier
        # Prefer strong contest; if none, grab the closest we can.
        key = (-contest if contest > 0 else contest, myd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    desired_dx = sgn(tx - sx)
    desired_dy = sgn(ty - sy)

    best_move = (0, 0)
    best_move_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        nd = cheb(nx, ny, tx, ty)
        # Tie-break: align with desired direction; prefer smaller opponent distance to same target.
        no = cheb(nx, ny, tx, ty)
        myd_next = nd
        od_next = cheb(ox, oy, tx, ty)
        align = (dx != desired_dx) + (dy != desired_dy)
        key = (nd, align, od_next - myd_next, dx, dy)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]