def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = set((p[0], p[1]) for p in obstacles)
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h
    if resources:
        best = None
        for r in resources:
            rx, ry = r[0], r[1]
            ds = dist((sx, sy), (rx, ry))
            do = dist((ox, oy), (rx, ry))
            score = ds - 0.55 * do  # prefer resources we can get sooner
            if best is None or score < best[0] or (score == best[0] and ds < best[1]):
                best = (score, ds, rx, ry)
        tx, ty = best[2], best[3]
    else:
        # No visible resources: move to center-right toward likely future/contest
        tx, ty = (w - 1) // 2, (h - 1) // 2
        if dist((sx, sy), (tx, ty)) < dist((sx, sy), (ox, oy)):
            tx, ty = ox, oy
    best_move = (0, 0)
    best_d = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue
        d = dist((nx, ny), (tx, ty))
        # small bias: if tie, prefer moving away from opponent when close
        opp_close = dist((nx, ny), (ox, oy))
        bias = 0
        if dist((sx, sy), (ox, oy)) <= 1 and opp_close >= 2:
            bias = -0.01
        if best_d is None or d + bias < best_d:
            best_d = d + bias
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]