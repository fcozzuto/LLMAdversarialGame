def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])
    if not resources:
        return [0, 0]

    def cheb(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Choose resource: strongly prefer those we can arrive strictly earlier.
    best_r = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        ds = cheb((sx, sy), (rx, ry))
        do = cheb((ox, oy), (rx, ry))
        # key: earlier-first, then minimize our distance, then block opponent (larger do), then tie by position
        key = (0 if ds < do else 1, ds, -do, rx, ry, rx + 7 * ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = (0, 0)
    best_m_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_us = cheb((nx, ny), (tx, ty))
        d_op = cheb((ox, oy), (tx, ty))
        # key: maximize chance to be earlier next step; then get closer to target; then avoid letting opponent get closer to target
        key = (0 if d_us < d_op else 1, d_us, d_op, -dx, -dy, nx, ny)
        if best_m_key is None or key < best_m_key:
            best_m_key = key
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]