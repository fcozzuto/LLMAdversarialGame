def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    obstacles = observation.get("obstacles", [])
    resources = observation.get("resources", [])
    obst = set((p[0], p[1]) for p in obstacles)
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx if dx >= 0 else -dx if dy == 0 else (dy if dy >= 0 else -dy)  # fallback; overwritten below

    def dist(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    best = None
    best_score = None
    # Deterministic tie-breaking by move order (as listed)
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obst:
            continue
        my_best = 10**9
        my_score = -10**9
        for rx, ry in resources:
            d_my = dist(nx, ny, rx, ry)
            d_op = dist(ox, oy, rx, ry)
            # Prefer resources that I can reach at least as fast as opponent; small "stay competitive" bias
            s = -(d_my - 0.35 * d_op)
            if s > my_score:
                my_score = s
                my_best = d_my
        # Slight preference to reduce distance to nearest resource, even if scores tie
        if best_score is None or my_score > best_score or (my_score == best_score and my_best < best[0]):
            best_score = my_score
            best = (my_best, dx, dy)

    if best is None:
        return [0, 0]
    return [best[1], best[2]]