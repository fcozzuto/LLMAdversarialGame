def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def kdist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy  # Chebyshev

    best_key = None
    tx = ty = resources[0][0], resources[0][1]
    for rx, ry in resources:
        myd = kdist(sx, sy, rx, ry)
        opd = kdist(ox, oy, rx, ry)
        key = (opd - myd, -myd, -rx, -ry, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            tx, ty = rx, ry

    deltas = [(-1, -1), (0, -1), (1, -1),
              (-1, 0), (0, 0), (1, 0),
              (-1, 1), (0, 1), (1, 1)]

    best_move = None
    best_val = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        myd2 = kdist(nx, ny, tx, ty)
        # Prefer closer to target, but also avoid being about to be out-raced
        opd2 = kdist(ox, oy, tx, ty)
        val = (opd2 - myd2, -myd2, dx, dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]