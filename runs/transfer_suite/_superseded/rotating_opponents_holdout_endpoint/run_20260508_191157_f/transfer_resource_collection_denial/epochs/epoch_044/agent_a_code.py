def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def manh(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    obs_set = set((x, y) for x, y in obstacles)
    if not resources:
        return [0, 0]

    best_t = None
    best_k = None
    for rx, ry in resources:
        sd = manh(sx, sy, rx, ry)
        od = manh(ox, oy, rx, ry)
        k = (od - sd, -sd, -rx - ry, -rx, -ry)
        if best_k is None or k > best_k:
            best_k = k
            best_t = (rx, ry)
    tx, ty = best_t

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def next_best_key(nx, ny):
        sd = manh(nx, ny, tx, ty)
        # Prefer breaking ties by being closer to the best alternative resource if we can't progress.
        other = None
        other_d = 10**9
        for rx, ry in resources:
            if (rx, ry) == (tx, ty):
                continue
            d = manh(nx, ny, rx, ry)
            if d < other_d:
                other_d = d
                other = (rx, ry)
        # Also incorporate immediate opponent pressure.
        od = manh(ox, oy, tx, ty)
        return (od - sd, -sd, -other_d if other else -10**9, nx - sx, ny - sy)

    best_move = [0, 0]
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        k = next_best_key(nx, ny)
        if best_key is None or k > best_key:
            best_key = k
            best_move = [dx, dy]

    if best_key is None:
        return [0, 0]
    return best_move