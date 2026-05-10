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

    def kdist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def best_target():
        best = None
        for rx, ry in resources:
            myd = kdist(sx, sy, rx, ry)
            opd = kdist(ox, oy, rx, ry)
            cand = (opd - myd, -myd, -rx, -ry, rx, ry)
            if best is None or cand > best:
                best = cand
        return best[4], best[5]

    tx, ty = best_target()

    def step_options():
        return [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    desired_dx = 0 if tx == sx else (1 if tx > sx else -1)
    desired_dy = 0 if ty == sy else (1 if ty > sy else -1)

    def valid(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs

    best_move = [0, 0]
    best_score = None
    for dx, dy in step_options():
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = kdist(nx, ny, tx, ty)
        align = 1 if (dx, dy) == (desired_dx, desired_dy) else 0
        cand = (-d, -align, dx, dy)
        if best_score is None or cand > best_score:
            best_score = cand
            best_move = [dx, dy]

    # If somehow all blocked (shouldn't happen), stay.
    return best_move if best_move is not None else [0, 0]