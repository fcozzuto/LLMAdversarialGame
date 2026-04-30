def choose_move(observation):
    w = observation.get('grid_width', 8)
    h = observation.get('grid_height', 8)
    sx, sy = observation['self_position']
    ox, oy = observation['opponent_position']
    resources = observation.get('resources', [])
    obstacles = set(tuple(p) for p in observation.get('obstacles', []))

    def dist2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(0, 0), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]

    if not resources:
        return [0, 0]

    # Choose a resource where we are relatively closer than opponent; otherwise nearest.
    best_r = None
    best_key = None
    for r in resources:
        rx, ry = r
        if (rx, ry) in obstacles:
            continue
        d_self = dist2((sx, sy), (rx, ry))
        d_opp = dist2((ox, oy), (rx, ry))
        # Prefer higher advantage; then closer.
        key = (-(d_opp - d_self), d_self, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)

    if best_r is None:
        return [0, 0]
    tx, ty = best_r

    # Among feasible moves, pick one minimizing distance to target; break ties deterministically.
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        val = (dist2((nx, ny), (tx, ty)), dx, dy)
        # Small extra pressure: if we would collide with opponent, slightly penalize.
        if (nx, ny) == (ox, oy):
            val = (val[0] + 1, val[1], val[2])
        if best_val is None or val < best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]