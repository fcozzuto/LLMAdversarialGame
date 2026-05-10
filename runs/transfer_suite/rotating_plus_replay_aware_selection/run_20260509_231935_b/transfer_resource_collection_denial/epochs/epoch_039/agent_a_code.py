def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    resources_list = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    res = set((p[0], p[1]) for p in resources_list)
    obs = set((p[0], p[1]) for p in obstacles_list)

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist8(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Prefer immediate pickup
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) in res and (nx, ny) not in obs:
            return [dx, dy]

    if not resources_list:
        return [0, 0]

    # Pick best target based on who reaches first
    best = None
    best_key = None
    for rx, ry in res:
        if (rx, ry) in obs:
            continue
        sd = dist8(sx, sy, rx, ry)
        od = dist8(ox, oy, rx, ry)
        key = (od - sd, -sd)  # first: maximize advantage, then minimize our distance
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # Choose move that best improves our advantage and reduces distance; avoid obstacles
    best_move = [0, 0]
    best_move_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        if (nx, ny) in res:
            return [dx, dy]
        sd2 = dist8(nx, ny, tx, ty)
        od2 = dist8(ox, oy, tx, ty)
        # Encourage steering, discourage getting stuck
        key = (od2 - sd2, -sd2, -dist8(nx, ny, tx, ty))
        if best_move_key is None or key > best_move_key:
            best_move_key = key
            best_move = [dx, dy]

    return best_move