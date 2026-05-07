def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs_set = set((p[0], p[1]) for p in obstacles)

    def king_dist(ax, ay, bx, by):
        dx = abs(ax - bx)
        dy = abs(ay - by)
        return dx if dx > dy else dy

    best_t = None
    for rx, ry in resources:
        my_d = king_dist(sx, sy, rx, ry)
        op_d = king_dist(ox, oy, rx, ry)
        key = (my_d - op_d, my_d, rx, ry)
        if best_t is None or key < best_t[0]:
            best_t = (key, (rx, ry))
    tx, ty = best_t[1]

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    best_m = (None, [0, 0])
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue
        my_next = king_dist(nx, ny, tx, ty)
        op_next = king_dist(ox, oy, tx, ty)
        key = (my_next - op_next, my_next, nx, ny)
        if best_m[0] is None or key < best_m[0]:
            best_m = (key, [dx, dy])
    return best_m[1]