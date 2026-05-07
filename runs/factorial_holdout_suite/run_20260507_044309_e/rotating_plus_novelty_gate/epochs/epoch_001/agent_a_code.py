def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    resources = observation["resources"]
    if not resources:
        return [0, 0]

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy  # Chebyshev distance

    # Prefer resources we can reach sooner than opponent (or at least closest to us)
    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        key = (ds - do, ds, rx, ry)  # deterministic tie-break
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = None
    best_m_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d = dist((nx, ny), (tx, ty))
        # Also prefer not stepping closer to opponent unless it helps reaching target
        opp_d = dist((nx, ny), (ox, oy))
        key = (d, -opp_d, dx, dy)
        if best_m_key is None or key < best_m_key:
            best_m_key = key
            best_m = (dx, dy)

    if best_m is None:
        return [0, 0]
    return [int(best_m[0]), int(best_m[1])]