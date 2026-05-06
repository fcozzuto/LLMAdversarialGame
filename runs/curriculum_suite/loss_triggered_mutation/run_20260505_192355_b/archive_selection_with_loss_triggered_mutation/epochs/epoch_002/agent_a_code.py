def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    moves = [(-1,-1), (0,-1), (1,-1), (-1,0), (0,0), (1,0), (-1,1), (0,1), (1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_step_to(tx, ty):
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = cheb(nx, ny, tx, ty)
            # deterministic tie-break: smaller distance, then prefer x movement, then y, then dx/dy values
            tie = (abs(dx), abs(dy), dx, dy)
            cand = (d, tie)
            if best is None or cand < best[0]:
                best = (cand, (dx, dy))
        if best is None:
            return [0, 0]
        return [best[1][0], best[1][1]]

    if not resources:
        tx, ty = w // 2, h // 2
        return best_step_to(tx, ty)

    best_r = None
    # Choose a resource where we have advantage (lower cheb distance than opponent)
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        adv = opd - myd  # higher is better
        cand = (-adv, myd, rx, ry)  # invert adv for min
        if best_r is None or cand < best_r[0]:
            best_r = (cand, (rx, ry))
    tx, ty = best_r[1]

    return best_step_to(tx, ty)