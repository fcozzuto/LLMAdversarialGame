def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    deltas = [(-1, 0), (1, 0), (0, -1), (0, 1),
              (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def mdist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    valid = []
    for rx, ry in resources:
        if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
            valid.append((rx, ry))
    if not valid:
        return [0, 0]

    best_t = None
    for rx, ry in valid:
        myd = mdist(sx, sy, rx, ry)
        od = mdist(ox, oy, rx, ry)
        advantage = od - myd
        # Prefer: higher advantage (we arrive earlier), then smaller myd, then deterministic tie-break
        key = (advantage, -myd, -rx, -ry)
        if best_t is None or key > best_t[0]:
            best_t = (key, rx, ry)
    _, tx, ty = best_t

    best_move = None
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        myd2 = mdist(nx, ny, tx, ty)
        od = mdist(ox, oy, tx, ty)
        advantage2 = od - myd2
        # If we can't reach quickly, still head toward a better resource via local progress
        key = (advantage2, -myd2, dx, dy, nx, ny)
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    if best_move is None:
        return [0, 0]
    return best_move