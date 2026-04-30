def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1),  (0, 0),  (0, 1),
             (1, -1),  (1, 0),  (1, 1)]

    def valid(nx, ny):
        return inb(nx, ny) and (nx, ny) not in obstacles

    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d_o = cheb(nx, ny, ox, oy)
            key = (-d_o, nx, ny)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1] if best is not None else [0, 0]

    best_r = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        gap = opd - myd  # positive means we are closer
        # Avoid clearly contested picks: prefer our lead, then closer, then deterministic.
        key = (-gap, myd, opd, rx, ry)
        # Want maximum gap => minimize -gap
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry, gap, myd)

    rx, ry, gap, myd = best_r if best_r is not None else (ox, oy, 0, cheb(sx, sy, ox, oy))

    # Move one step to improve our position toward the target while reducing/limiting opponent advantage.
    best = None
    cur_my = cheb(sx, sy, rx, ry)
    cur_op = cheb(ox, oy, rx, ry)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd_my = cheb(nx, ny, rx, ry)
        # opponent's distance to target stays unless they move; we instead use our own progress and gap change
        new_gap = cur_op - nd_my
        # Prefer: increase gap; then reduce our distance; then keep away from opponent a bit; deterministic by coord.
        d_o_from_opp = cheb(nx, ny, ox, oy)
        key = (-new_gap, nd_my, d_o_from_opp, nx, ny)
        if best is None or key < best[0]:
            best = (key, [dx, dy])

    return best[1] if best is not None else [0, 0]