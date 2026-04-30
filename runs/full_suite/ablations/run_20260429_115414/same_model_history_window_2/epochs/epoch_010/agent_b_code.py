def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    blocked = set((p[0], p[1]) for p in obstacles)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def legal(x, y): return inb(x, y) and (x, y) not in blocked
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = -dx if dx < 0 else dx
        dy = y1 - y2; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    viable = []
    for r in resources:
        rx, ry = r[0], r[1]
        if legal(rx, ry):
            myd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer: I can get earlier by margin; then smaller myd; then closer to their parity; then deterministic tie.
            viable.append((rx, ry, od - myd, myd, abs((rx + ry) - (sx + sy)), -rx, -ry))
    if viable:
        viable.sort(key=lambda t: (-t[2], t[3], t[4], t[5], t[6]))
        tx, ty = viable[0][0], viable[0][1]
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        # Extra: penalize moves that give opponent a closer path to same target.
        nod = cheb(ox, oy, tx, ty)
        my_adv = nod - nd
        key = (my_adv, -nd, -abs((nx + ny) - (sx + sy)), dx, dy)
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)

    if best_key is None:
        # All neighbors blocked: stay put deterministically.
        return [0, 0]
    return [best[0], best[1]]