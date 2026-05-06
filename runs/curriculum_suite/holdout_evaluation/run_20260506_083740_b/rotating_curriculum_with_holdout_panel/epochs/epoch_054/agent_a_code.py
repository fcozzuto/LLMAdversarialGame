def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    ob = set()
    for p in obstacles:
        if p and len(p) >= 2:
            ob.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in ob

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    res_list = []
    for r in resources:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            res_list.append((rx, ry))
    if not res_list:
        best = None
        bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = dist(nx, ny, ox, oy)
            if v > bestv:
                bestv, best = v, [dx, dy]
        return best if best is not None else [0, 0]

    best_target = None
    best_key = None
    for rx, ry in res_list:
        dme = dist(sx, sy, rx, ry)
        dome = dist(ox, oy, rx, ry)
        key = (dme > dome, -(dme - dome), dme)
        if best_key is None or key > best_key:
            best_key, best_target = key, (rx, ry)

    tx, ty = best_target
    best = [0, 0]
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd = dist(nx, ny, tx, ty)
        oppd = dist(nx, ny, ox, oy)
        v = -myd * 10 + oppd
        if (dx == 0 and dy == 0):
            v -= 0.1
        if v > bestv:
            bestv, best = v, [dx, dy]
    return best