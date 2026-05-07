def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    cand = [(-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)]

    def dist(a, b, c, d):
        dx, dy = abs(a - c), abs(b - d)
        return dx if dx > dy else dy  # Chebyshev for diagonal movement

    if resources:
        best_res = None
        best_key = None
        for rx, ry in resources:
            sd = dist(sx, sy, rx, ry)
            od = dist(ox, oy, rx, ry)
            key = (od - sd, -sd)  # maximize advantage; if tie, smaller self distance
            if best_key is None or key > best_key:
                best_key = key
                best_res = (rx, ry)
        tx, ty = best_res
    else:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        tx, ty = max(corners, key=lambda p: (dist(sx, sy, p[0], p[1]) - dist(ox, oy, p[0], p[1]), -p[0], -p[1]))

    best_move = [0, 0]
    best_key = None
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        sd = dist(nx, ny, tx, ty)
        od = dist(ox, oy, tx, ty)  # opponent not moving this turn
        # Prefer moves that keep our advantage and reduce our distance to the target.
        key = (od - sd, -sd, -dist(nx, ny, ox, oy))
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]
    return best_move if best_move is not None else [0, 0]