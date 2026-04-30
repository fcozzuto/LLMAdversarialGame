def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    res = [(x, y) for (x, y) in resources if inb(x, y) and (x, y) not in obstacles]
    if not res:
        # fallback: move to maximize distance from opponent
        best = None
        bestv = -10**9
        for dx, dy, nx, ny in legal:
            v = cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    t = observation.get("turn_index", 0)
    if t % 2 == 0:
        target = min(res, key=lambda r: cheb(sx, sy, r[0], r[1]))
    else:
        # diversify: pick resource that is good for us but bad for opponent
        target = min(res, key=lambda r: cheb(sx, sy, r[0], r[1]) - cheb(ox, oy, r[0], r[1]))

    tx, ty = target
    dx_sign = 0 if tx == sx else (1 if tx > sx else -1)
    dy_sign = 0 if ty == sy else (1 if ty > sy else -1)

    best = None
    best_score = -10**18
    for dx, dy, nx, ny in legal:
        # prefer moving roughly toward target, then minimizing distance
        toward = 0
        if dx == dx_sign: toward += 1
        if dy == dy_sign: toward += 1
        score = toward * 10 - cheb(nx, ny, tx, ty)
        if score > best_score:
            best_score = score
            best = (dx, dy)
    return [best[0], best[1]]