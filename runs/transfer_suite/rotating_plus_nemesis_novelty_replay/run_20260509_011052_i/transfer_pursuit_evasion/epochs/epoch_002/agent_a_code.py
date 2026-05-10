def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obs = observation.get("obstacles", [])
    obstacles = set()
    for o in obs:
        obstacles.add((o[0], o[1]))

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0),  (0, 0),  (1, 0),
            (-1, 1),  (0, 1),  (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best = None
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist = abs(nx - ox)
        d2 = abs(ny - oy)
        if d2 > dist:
            dist = d2  # Chebyshev distance
        # Prefer immediate capture, then shorter distance, then deterministic tie-break by dx,dy order.
        capture = 1 if (nx == ox and ny == oy) else 0
        key = (-capture, dist, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best