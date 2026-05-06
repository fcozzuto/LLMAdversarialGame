def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not valid(sx, sy):
        for yy in range(h):
            for xx in range(w):
                if valid(xx, yy):
                    sx, sy = xx, yy
                    break
            if valid(sx, sy):
                break

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if valid(x, y):
                resources.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_move = [0, 0]
    best_val = None

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nres = md((nx, ny), resources[0]) if resources else 0
        if resources:
            dmin = 10**9
            for r in resources:
                d = md((nx, ny), r)
                if d < dmin:
                    dmin = d
            nres = dmin
        ndopp = md((nx, ny), (ox, oy))
        val = 0
        if resources:
            val += -nres * 3
            val += -(md((sx, sy), resources[0]) if False else 0)
        val += ndopp * 1
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    if not valid(sx + best_move[0], sy + best_move[1]):
        for dx, dy in moves:
            if valid(sx + dx, sy + dy):
                return [dx, dy]
    return best_move