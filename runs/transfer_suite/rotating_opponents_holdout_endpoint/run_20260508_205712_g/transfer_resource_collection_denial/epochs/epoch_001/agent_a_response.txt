def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation["obstacles"])
    resources = observation["resources"]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx + dy

    if not resources:
        # No targets: move toward opponent slightly to contest.
        tx, ty = ox, oy
    else:
        # Choose a deterministic nearest resource; break ties by (x,y).
        best = None
        for rx, ry in resources:
            d = dist((sx, sy), (rx, ry))
            cand = (d, rx, ry)
            if best is None or cand < best:
                best = cand
        tx, ty = best[1], best[2]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    # Deterministic scoring: prefer closer to target; then avoid obstacles; then reduce distance to opponent for pressure.
    scored = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            # Engine will keep position; treat as worst.
            scored.append((10**9, 0, 0, 0, dx, dy))
            continue
        d_t = dist((nx, ny), (tx, ty))
        d_o = dist((nx, ny), (ox, oy))
        # Extra bias: if multiple resources, try to move along the faster axis (lower max-step direction).
        axis_bias = min(abs(tx - nx), abs(ty - ny))
        scored.append((d_t, axis_bias, d_o, 0, dx, dy))

    scored.sort(key=lambda z: (z[0], z[1], z[2], z[3], z[4], z[5]))
    dx, dy = scored[0][4], scored[0][5]
    return [dx, dy]