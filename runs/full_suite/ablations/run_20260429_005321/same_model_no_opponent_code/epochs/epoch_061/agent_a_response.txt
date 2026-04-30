def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []

    obs = {(p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) >= 2}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]
    cands = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            cands.append((dx, dy, nx, ny))

    if not cands:
        return [0, 0]

    if not resources:
        best = None
        bestv = -10**18
        for dx, dy, nx, ny in cands:
            v = -cheb(nx, ny, ox, oy)
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    best = None
    bestv = -10**18
    for dx, dy, nx, ny in cands:
        # Value is best targeting among resources after this move.
        my_to_op = cheb(nx, ny, ox, oy)
        local_best = -10**18
        for rx, ry in resources:
            sdist = cheb(nx, ny, rx, ry)
            odist = cheb(ox, oy, rx, ry)
            advantage = odist - sdist  # positive => we are closer
            v = (1000 - 5 * sdist) + 25 * advantage - 2 * my_to_op
            if v > local_best:
                local_best = v
        if local_best > bestv or (local_best == bestv and (dx, dy) < best):
            bestv = local_best
            best = (dx, dy)

    return [best[0], best[1]]