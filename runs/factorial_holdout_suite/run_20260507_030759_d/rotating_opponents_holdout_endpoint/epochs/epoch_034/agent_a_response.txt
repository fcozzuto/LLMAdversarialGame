def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and valid(x, y):
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best_t = None
    best_cost = None
    for tx, ty in res:
        d1 = cheb(sx, sy, tx, ty)
        d2 = cheb(ox, oy, tx, ty)
        cost = d1 - 0.6 * d2
        if best_cost is None or cost < best_cost or (cost == best_cost and (d1 < cheb(sx, sy, best_t[0], best_t[1]) if best_t else True)):
            best_cost = cost
            best_t = (tx, ty)

    tx, ty = best_t
    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                moves.append((0, 0, 0, 0))
            else:
                nx, ny = sx + dx, sy + dy
                if valid(nx, ny):
                    moves.append((dx, dy, nx, ny))

    # Deterministic tie-breaking order: prefer smaller (dx,dy) lexicographically among equal scores
    best_m = (0, 0, sx, sy)
    best_s = None
    for dx, dy, nx, ny in moves:
        own_d = cheb(nx, ny, tx, ty)
        opp_d = cheb(ox, oy, nx, ny)
        # Prefer getting closer to target; slight preference to reduce being near opponent.
        s = own_d - 0.08 * opp_d
        if best_s is None or s < best_s or (s == best_s and (dx, dy) < (best_m[0], best_m[1])):
            best_s = s
            best_m = (dx, dy, nx, ny)

    return [int(best_m[0]), int(best_m[1])]