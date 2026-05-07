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

    # Pick a resource where we can get ahead (my distance relative to opponent)
    best = None
    for rx, ry in resources:
        my_d = king_dist(sx, sy, rx, ry)
        op_d = king_dist(ox, oy, rx, ry)
        # Prefer smaller (my_d - op_d); then smaller my_d; then deterministic x,y
        key = (my_d - op_d, my_d, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    tx, ty = best[1]

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    best_move = [0, 0]
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue
        my_next = king_dist(nx, ny, tx, ty)
        op_next = king_dist(ox, oy, tx, ty)
        # Encourage progress to target and discourage opponent closeness (deterministic tie-break)
        key = (my_next, -(op_next - my_next), dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]
    return best_move