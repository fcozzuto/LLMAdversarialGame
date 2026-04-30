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
        tx = w - 1 if (sx + ox) < (w - 1) else 0
        ty = h - 1 if (sy + oy) < (h - 1) else 0
        return [sgn(tx - sx), sgn(ty - sy)]

    best = None
    best_key = None
    for rx, ry in viable:
        myd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        contest = od - myd  # positive => we are earlier
        # Prefer resources we can contest, and then those far from opponent (to reduce their chances).
        op_dist = abs(ox - rx) + abs(oy - ry)
        # Also bias toward the diagonal "belt" closer to our corner.
        my_bias = abs((rx + ry) - (sx + sy))
        # Key: maximize contest, then maximize opponent distance, then minimize my distance.
        key = (-contest, -op_dist, myd, my_bias, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # Choose next step that maximizes contest after move.
    best_move = (0, 0)
    best_move_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        myd2 = cheb(nx, ny, tx, ty)
        od2 = cheb(ox, oy, tx, ty)
        contest2 = od2 - myd2
        # If equal contest, minimize distance to target; then keep deterministic ordering.
        # (Opponent distance to the target remains od2, so contest2 is sufficient.)
        key = (-contest2, myd2, abs(nx - tx) + abs(ny - ty), dx, dy)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]