def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        win = 1 if myd < opd else (0 if myd == opd else -1)
        # Prefer: being closer, then smaller myd, then being even more ahead vs opponent.
        key = (win, -(opd - myd), -myd, -rx, -ry)
        if best is None or key > best[0]:
            best = (key, rx, ry)
    tx, ty = best[1], best[2]

    best_move = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(ox, oy, tx, ty)
        ahead = 1 if myd2 < opd2 else (0 if myd2 == opd2 else -1)
        dist_to_target = -myd2
        # Mild preference to reduce distance to opponent when we are not ahead (deny contest).
        deny = -(cheb(nx, ny, ox, oy)) if ahead < 1 else 0
        val = (ahead, dist_to_target, -(opd2 - myd2), deny, -dx, -dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]