def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation.get("obstacles", []))
    resources = observation.get("resources", [])

    def clamp(nx, ny):
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            return sx, sy
        if (nx, ny) in obstacles:
            return sx, sy
        return nx, ny

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick a target resource by who is closer; prefer large advantage, else still go for nearest.
    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        adv = do - ds  # positive means we are closer
        key = (adv, -ds, -do, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        # No resources: head toward center-ish to stay flexible and avoid edges.
        tx, ty = w // 2, h // 2
    else:
        tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]

    do0 = cheb(ox, oy, tx, ty)
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        ds1 = cheb(nx, ny, tx, ty)
        adv1 = do0 - ds1
        # Strongly favor increasing advantage; then decreasing distance; discourage staying if not needed.
        dist_pen = ds1
        stay_pen = 1 if (nx == sx and ny == sy) else 0
        score = 10 * adv1 - dist_pen - 2 * stay_pen
        # If negative advantage for all, still pick move minimizing our distance to the target.
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]