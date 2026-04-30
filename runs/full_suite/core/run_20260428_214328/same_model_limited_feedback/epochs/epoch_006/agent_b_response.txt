def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])

    obs_set = set()
    for x, y in obstacles:
        if 0 <= x < w and 0 <= y < h:
            obs_set.add((x, y))

    def sqdist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    if resources:
        best_t = None
        best_val = None
        for tx, ty in resources:
            dv = sqdist((sx, sy), (tx, ty)) - 0.9 * sqdist((ox, oy), (tx, ty))
            if best_val is None or dv < best_val:
                best_val = dv
                best_t = (tx, ty)
        target = best_t
    else:
        target = (w // 2, h // 2)

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs_set:
                moves.append((dx, dy, nx, ny))

    if not moves:
        return [0, 0]

    best_move = None
    best_cost = None
    for dx, dy, nx, ny in moves:
        d_t = sqdist((nx, ny), target)
        d_o = sqdist((nx, ny), (ox, oy))
        center_boost = 0
        if 0 <= nx < w and 0 <= ny < h:
            cx, cy = w // 2, h // 2
            center_boost = 0.02 * sqdist((nx, ny), (cx, cy))
        cost = d_t - 0.55 * d_o + center_boost
        if best_cost is None or cost < best_cost:
            best_cost = cost
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]