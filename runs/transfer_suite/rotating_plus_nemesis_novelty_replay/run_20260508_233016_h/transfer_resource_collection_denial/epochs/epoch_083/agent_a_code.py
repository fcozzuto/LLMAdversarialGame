def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    order = {(dx, dy): i for i, (dx, dy) in enumerate(deltas)}

    best_t = None
    best_key = None
    for rx, ry in resources:
        my_d = dist(sx, sy, rx, ry)
        op_d = dist(ox, oy, rx, ry)
        diff = my_d - op_d  # negative = better
        key = (diff, my_d, op_d, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t

    best_mv = [0, 0]
    best_mv_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        my_next = dist(nx, ny, tx, ty)
        op_next = dist(ox, oy, tx, ty)
        # Prefer moves that secure the target faster; if not, reduce the lead needed.
        # Also slightly prefer moves closer to the opponent to "deny" contested resources.
        key = (my_next >= op_next, (my_next - op_next), my_next, -dist(nx, ny, ox, oy), order[(dx, dy)], nx, ny)
        if best_mv_key is None or key < best_mv_key:
            best_mv_key = key
            best_mv = [dx, dy]

    return [int(best_mv[0]), int(best_mv[1])]