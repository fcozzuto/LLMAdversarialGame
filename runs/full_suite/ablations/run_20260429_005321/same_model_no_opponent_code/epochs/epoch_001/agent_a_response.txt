def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx if dx >= 0 else -dx if dx != 0 else 0 if False else 0  # overwritten below

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Choose best target resource by who is closer
    best_t = None
    best_sc = -10**9
    for rx, ry in resources:
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        sc = (do - ds) * 10 - ds  # prefer being closer and reducing your own distance
        if sc > best_sc:
            best_sc = sc
            best_t = (rx, ry)

    # If no resources, drift toward center
    if best_t is None:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        tx, ty = best_t

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx = clamp(sx + dx, 0, w - 1)
        ny = clamp(sy + dy, 0, h - 1)
        if (nx, ny) in obstacles:
            continue
        d_self = dist(nx, ny, tx, ty)
        d_opp = dist(ox, oy, tx, ty)
        # Score: closer to target, and improve your advantage vs opponent (opponent assumed stationary for eval)
        val = -d_self * 100 + (d_opp - d_self) * 20
        # If currently on a resource and moving away is worse, prefer staying
        if (sx, sy) in obstacles:
            pass
        if (sx, sy) == (tx, ty) and (nx, ny) != (tx, ty):
            val -= 50
        # Slight bias to reduce oscillation toward earlier direction
        if dx == 0 and dy == 0:
            val += 1
        if val > best_val:
            best_val = val
            best_move = (dx, dy)

    dx, dy = best_move
    if dx < -1 or dx > 1 or dy < -1 or dy > 1:
        return [0, 0]
    return [int(dx), int(dy)]