def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    blocked = set((p[0], p[1]) for p in obstacles)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy
    def legal(x, y): return inb(x, y) and (x, y) not in blocked

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    viable = []
    for r in resources:
        rx, ry = r[0], r[1]
        if legal(rx, ry):
            myd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            viable.append((rx, ry, myd, od, od - myd))
    if viable:
        good = [t for t in viable if t[4] >= 2]
        pool = good if good else viable
        # prefer clearly earlier arrival; then closer
        best = min(pool, key=lambda t: (-t[4], t[2], abs((t[0]+t[1]) - (sx+sy)), t[0], t[1]))
        tx, ty = best[0], best[1]
    else:
        # no usable resource: drift toward center to avoid being boxed in
        tx, ty = w//2, h//2

    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        myd2 = cheb(nx, ny, tx, ty)
        od2 = cheb(ox, oy, tx, ty)
        # maximize immediate contest pressure; then minimize distance to target
        key = (- (od2 - myd2), myd2, abs(nx - tx) + abs(ny - ty), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]