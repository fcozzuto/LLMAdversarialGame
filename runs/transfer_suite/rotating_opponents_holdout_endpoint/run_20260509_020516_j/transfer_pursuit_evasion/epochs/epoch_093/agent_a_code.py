def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    role = str(observation.get("self_role", "")).lower()
    is_evader = ("evader" in role) and ("pursuer" not in role)

    obstacles = set()
    for it in observation.get("obstacles") or []:
        try:
            if isinstance(it, dict):
                x, y = it.get("x"), it.get("y")
            else:
                x, y = it[0], it[1]
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not ok(sx, sy):
        sx = max(0, min(w - 1, sx))
        sy = max(0, min(h - 1, sy))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    neigh4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def man(x, y, a, b):
        return abs(x - a) + abs(y - b)

    corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
    far_corner = max(corners, key=lambda c: man(c[0], c[1], ox, oy))

    def obstacle_proximity(x, y):
        p = 0
        for dx, dy in neigh4:
            if (x + dx, y + dy) in obstacles:
                p += 1
        return p

    best = None
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = man(nx, ny, ox, oy)
        prox = obstacle_proximity(nx, ny)
        corner_bias = man(nx, ny, far_corner[0], far_corner[1])
        if is_evader:
            # maximize distance from pursuer, avoid walls/obstacles, also steer toward farthest corner
            score = (d * 100) - (prox * 20) - corner_bias
            better = best_score is None or score > best_score
        else:
            # minimize distance to evader, avoid being boxed in
            score = -(d * 100) - (prox * 10) + (-corner_bias)
            better = best_score is None or score > best_score
        if better:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]