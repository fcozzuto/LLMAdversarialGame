def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def kdist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy  # Chebyshev

    def move_toward(tx, ty):
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return dx, dy

    # Target resource: maximize (opponent arrival - my arrival); tie-break by faster my arrival and deterministic ordering.
    best = None
    for rx, ry in resources:
        myd = kdist(sx, sy, rx, ry)
        opd = kdist(ox, oy, rx, ry)
        cand = (opd - myd, -myd, -rx, -ry, rx, ry)
        if best is None or cand > best:
            best = cand
    tx, ty = best[4], best[5]

    # If direct step is blocked, choose the best valid move among 9 deltas by same objective locally.
    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    dx0, dy0 = move_toward(tx, ty)

    best_move = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        myd2 = kdist(nx, ny, tx, ty)
        opd2 = kdist(ox, oy, tx, ty)
        cand = (opd2 - myd2, -myd2, abs(dx - dx0) + abs(dy - dy0), -dx, -dy)
        if best_move is None or cand > best_move:
            best_move = cand
    if best_move is None:
        return [0, 0]
    dx_ans, dy_ans = -best_move[3], -best_move[4]
    return [int(dx_ans), int(dy_ans)]