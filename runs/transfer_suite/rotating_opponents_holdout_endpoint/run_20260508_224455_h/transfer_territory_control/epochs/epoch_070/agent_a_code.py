def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0: w = 8
    if h <= 0: h = 8
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles") or []
    obst = set()
    for c in obstacles:
        if isinstance(c, (list, tuple)) and len(c) >= 2:
            obst.add((int(c[0]), int(c[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return not inside(x, y) or (x, y) in obst

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]
    best = (10**9, None, None)  # (dist, penalty, dir)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        dist = abs(nx - ox) + abs(ny - oy)
        penalty = (dx == 0 and dy == 0)
        key = (dist, penalty)
        if key < (best[0], best[1]):
            best = (dist, penalty, (dx, dy))

    if best[2] is not None:
        return [int(best[2][0]), int(best[2][1])]

    # If all moves blocked, stay put (if valid) else move any in-bounds non-obstacle.
    if not blocked(sx, sy):
        return [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not blocked(nx, ny):
            return [int(dx), int(dy)]
    return [0, 0]