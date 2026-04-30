def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))
    resources = observation.get("resources", [])
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def dist2(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx * dx + dy * dy

    def best_value(nx, ny):
        bv = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = dist2(nx, ny, rx, ry)
            oppd = dist2(ox, oy, rx, ry)
            val = (oppd - ds) - 0.01 * ds
            if val > bv:
                bv = val
        return bv

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        v = best_value(nx, ny)
        if v > best_val:
            best_val = v
            best_move = [dx, dy]

    return best_move