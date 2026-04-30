def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        obs.add((p[0], p[1]))
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def safe(x, y):
        return inb(x, y) and (x, y) not in obs

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if resources:
        best = None
        best_d = 10**9
        for r in resources:
            rx, ry = r[0], r[1]
            if not safe(rx, ry):
                continue
            d = man((sx, sy), (rx, ry))
            if d < best_d:
                best_d, best = d, (rx, ry)
        if best is not None:
            tx, ty = best
            oppd = man((ox, oy), (tx, ty))
            best_move = None
            best_val = -10**18
            for dx, dy in moves:
                nx, ny = sx + dx, sy + dy
                if not safe(nx, ny):
                    continue
                myd = man((nx, ny), (tx, ty))
                od = oppd if (nx, ny) == (ox, oy) else man((ox, oy), (tx, ty))
                val = -myd + 0.7 * (od - myd) - (1.5 if (nx, ny) == (ox, oy) else 0)
                if val > best_val:
                    best_val = val
                    best_move = [dx, dy]
            if best_move is not None:
                return best_move

    cx, cy = w // 2, h // 2
    target = (cx, cy)
    best_move = None
    best_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        val = -man((nx, ny), target) + 0.6 * man((nx, ny), (ox, oy)) - (0.5 if (nx, ny) == (ox, oy) else 0)
        if val > best_val:
            best_val = val
            best_move = [dx, dy]
    if best_move is None:
        return [0, 0]
    return best_move