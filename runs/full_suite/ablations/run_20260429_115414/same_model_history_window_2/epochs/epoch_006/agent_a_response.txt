def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    blocked = set((p[0], p[1]) for p in obstacles)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    viable = [(r[0], r[1]) for r in resources if inb(r[0], r[1]) and (r[0], r[1]) not in blocked]

    # Select target resource we can contest (or else nearest we can reach safely).
    if viable:
        best = None
        best_key = None
        for rx, ry in viable:
            myd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer us being earlier; then closer; then deterministic belt bias; then coord tie-break.
            belt = abs((rx + ry) - (sx + sy))
            key = (-(od - myd), myd, belt, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best
    else:
        # No resources: head toward the corner on our "outer" side (away from opponent).
        tx = 0 if sx > (w - 1) // 2 else (w - 1)
        ty = 0 if sy > (h - 1) // 2 else (h - 1)
        # choose the better of two candidate corners deterministically by cheb to opponent
        c1 = (0, h - 1)
        c2 = (w - 1, 0)
        if cheb(ox, oy, c1[0], c1[1]) < cheb(ox, oy, c2[0], c2[1]):
            tx, ty = c2
        else:
            tx, ty = c1

    # Choose move maximizing post-move contest; then minimize our distance; avoid obstacles/out-of-bounds.
    best_move = (0, 0)
    best_val = None
    myd0 = cheb(sx, sy, tx, ty)
    od0 = cheb(ox, oy, tx, ty)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            if (dx, dy) != (0, 0):
                continue
            nx, ny = sx, sy
        myd = cheb(nx, ny, tx, ty)
        # Positive if we are closer than opponent for this target.
        contest = od0 - myd
        # Bias: prefer progress (not increasing distance) and keep movement toward the target.
        progress = myd0 - myd
        # Also discourage stepping away from target belt for determinism.
        belt = abs(((nx + ny) - (tx + ty)))
        val = (-contest, -progress, belt, dx, dy)  # lexicographic min
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]