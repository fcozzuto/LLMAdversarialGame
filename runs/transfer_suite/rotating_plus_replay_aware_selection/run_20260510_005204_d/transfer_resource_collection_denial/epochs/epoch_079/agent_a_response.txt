def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best_key = None
    tx = ty = resources[0][0], resources[0][1]
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach no later than opponent; otherwise still grab the best contestable one.
        key = (myd - opd, myd, -abs(ry - oy), -rx, -ry)
        if best_key is None or key < best_key:
            best_key = key
            tx, ty = rx, ry

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        score = (cheb(nx, ny, tx, ty), 0 if (nx, ny) == (tx, ty) else 1, abs(dx) + abs(dy))
        if best_m is None or score < best_m[0]:
            best_m = (score, dx, dy)
    if best_m is None:
        return [0, 0]
    return [best_m[1], best_m[2]]