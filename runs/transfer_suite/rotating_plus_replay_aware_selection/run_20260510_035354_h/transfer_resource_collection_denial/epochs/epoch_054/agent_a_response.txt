def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if (x, y) not in obs:
                res.append((x, y))

    if not res:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    best_target = None
    best_tkey = None
    for rx, ry in res:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        closer = 0 if ds < do else 1
        # Prefer getting it first; then closer distance; then deny opponent.
        tkey = (closer, ds, -do, rx, ry)
        if best_tkey is None or tkey < best_tkey:
            best_tkey, best_target = tkey, (rx, ry)

    tx, ty = best_target
    best_mkey = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) == (tx, ty):
            mkey = (-10**9, 0, 0, 0, dx, dy)
        else:
            ds2 = cheb(nx, ny, tx, ty)
            # Small tie-break to reduce oscillation: bias toward current target direction.
            dir_bias = abs((nx - tx)) + abs((ny - ty))
            mkey = (0, ds2, dir_bias, abs(dx) + abs(dy), dx, dy)
        if best_mkey is None or mkey < best_mkey:
            best_mkey, best_move = mkey, [dx, dy]

    return best_move