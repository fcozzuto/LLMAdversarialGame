def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    self_x, self_y = observation.get("self_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs_set = set((p[0], p[1]) for p in obstacles)
    if not resources:
        return [0, 0]

    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return max(dx, dy)

    # Pick nearest resource; tie-break by (dist, x, y)
    best = None
    for rx, ry in resources:
        d = dist((self_x, self_y), (rx, ry))
        key = (d, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))
    target = best[1]

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]
    # Deterministic tie-break: lowest (distance, dx, dy) among valid moves
    best_move = None
    best_key = None
    for dx, dy in deltas:
        nx, ny = self_x + dx, self_y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs_set:
            continue
        d = dist((nx, ny), target)
        key = (d, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    if best_move is None:
        return [0, 0]
    return best_move