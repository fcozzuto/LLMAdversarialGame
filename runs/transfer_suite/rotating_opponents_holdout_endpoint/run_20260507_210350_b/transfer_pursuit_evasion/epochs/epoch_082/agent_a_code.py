def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if p is not None and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in obs

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    resources = observation.get("resources") or []
    candidates = []
    for r in resources:
        if r is not None and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if legal(x, y):
                candidates.append((x, y))

    if candidates:
        best = None
        best_score = None
        for x, y in candidates:
            dme = man((sx, sy), (x, y))
            dop = man((ox, oy), (x, y))
            s = (dme - dop, dme, x, y)
            if best_score is None or s < best_score:
                best_score = s
                best = (x, y)
        tx, ty = best
    else:
        tx, ty = ox, oy

    best_move = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        val = (man((nx, ny), (tx, ty)), dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    if best_move is None:
        return [0, 0]
    return best_move