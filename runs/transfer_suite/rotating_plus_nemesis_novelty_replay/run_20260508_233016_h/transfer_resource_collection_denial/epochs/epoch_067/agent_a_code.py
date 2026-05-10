def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    resources = sorted((r[0], r[1]) for r in resources)
    best = None
    for rx, ry in resources:
        my_d = dist(sx, sy, rx, ry)
        op_d = dist(ox, oy, rx, ry)
        secure = my_d < op_d
        # Prefer securing; otherwise deny by maximizing our advantage (i.e., minimizing op_d-my_d).
        key = (0 if secure else 1, my_d if secure else (op_d - my_d), op_d if secure else my_d, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = None
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        my_to = dist(nx, ny, tx, ty)
        op_to = dist(ox, oy, tx, ty)
        my_vs_op = dist(nx, ny, tx, ty) - op_to  # lower is better
        # Intercept bias: try to reduce our distance to target and, when possible, also shorten opponent's relative access.
        intercept = dist(nx, ny, ox, oy) - dist(sx, sy, ox, oy)
        val = (my_to, my_vs_op, intercept, nx, ny)
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    if best_move is None:
        # If surrounded/blocked, stay.
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]