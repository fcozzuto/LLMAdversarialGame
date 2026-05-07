def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((x, y) for x, y in observation["obstacles"])
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    # Pick best resource by advantage; deterministic tie-break by position.
    best_cell = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        key = (od - sd, -sd, -(rx + 17 * ry))
        if best_key is None or key > best_key:
            best_key = key
            best_cell = (rx, ry)

    tx, ty = best_cell

    # Evaluate candidate moves with a stronger lookahead: keep/extend advantage.
    best_move = (0, 0)
    best_score = None
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny):
            continue
        sd2 = cheb(nx, ny, tx, ty)
        od2 = cheb(ox, oy, tx, ty)  # opponent position fixed during our move
        # Also consider improving distance to the next best alternative resource.
        alt_best = 10**9
        for rx, ry in resources:
            if (rx, ry) == (tx, ty):
                continue
            alt_best = min(alt_best, cheb(nx, ny, rx, ry))
        score = (od2 - sd2, -sd2, -alt_best, mx, my)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (mx, my)

    return [best_move[0], best_move[1]]