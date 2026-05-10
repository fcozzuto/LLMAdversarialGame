def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in (observation.get("resources", []) or []):
        resources.append((int(r[0]), int(r[1])))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def score_move(nx, ny):
        best_res = 10**9
        for rx, ry in resources:
            d = abs(nx - rx) + abs(ny - ry)
            if d < best_res:
                best_res = d
        if resources:
            return -best_res * 1000 - (abs(ox - nx) + abs(oy - ny))
        return -(abs(ox - nx) + abs(oy - ny))

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        tx, ty = resources[0]
        best = 10**9
        for rx, ry in resources:
            d = abs(sx - rx) + abs(sy - ry)
            if d < best:
                best = d
                tx, ty = rx, ry

    preferred_dx = 0 if tx == sx else (1 if tx > sx else -1)
    preferred_dy = 0 if ty == sy else (1 if ty > sy else -1)

    best_val = -10**18
    best_move = [0, 0]
    order = []
    for dx, dy in dirs:
        if dx == preferred_dx and dy == preferred_dy:
            order.insert(0, (dx, dy))
        else:
            order.append((dx, dy))

    for dx, dy in order:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            v = score_move(nx, ny)
            if v > best_val:
                best_val = v
                best_move = [dx, dy]

    return best_move