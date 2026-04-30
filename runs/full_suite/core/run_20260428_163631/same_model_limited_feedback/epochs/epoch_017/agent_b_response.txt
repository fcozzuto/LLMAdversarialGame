def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    best_r = None
    best_eff = None
    best_key = None
    for rx, ry in resources:
        d1 = cheb(x, y, rx, ry)
        d2 = cheb(ox, oy, rx, ry)
        if d1 <= d2:
            eff = d1
        else:
            eff = d1 + 3 * (d2 - d1) + 1
        key = (eff, rx, ry)
        if best_eff is None or key < best_key:
            best_eff = eff
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r
    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]
    best_move = (0, 0)
    best_dist = None
    best_move_key = None

    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        dist = cheb(nx, ny, tx, ty)
        mv_key = (dist, abs(dx) + abs(dy), dx, dy)
        if best_dist is None or mv_key < best_move_key:
            best_dist = dist
            best_move_key = mv_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]