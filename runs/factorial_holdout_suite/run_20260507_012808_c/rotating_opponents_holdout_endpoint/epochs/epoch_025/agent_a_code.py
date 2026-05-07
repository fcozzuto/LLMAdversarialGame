def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            val = man(nx, ny, ox, oy)
            cand = (val, nx, ny)
            if best is None or cand > best:
                best = cand
        if best is None:
            return [0, 0]
        nx, ny = best[1], best[2]
        return [nx - sx, ny - sy]

    best_t = None
    best_key = None
    for tx, ty in resources:
        sd = man(sx, sy, tx, ty)
        od = man(ox, oy, tx, ty)
        if od >= sd:
            key = (sd, tx, ty, od)
            if best_key is None or key < best_key:
                best_key = key
                best_t = (tx, ty)

    if best_t is None:
        best_t = min(resources, key=lambda p: (man(sx, sy, p[0], p[1]), p[0], p[1]))

    tx, ty = best_t
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = man(nx, ny, tx, ty)
        cand = (d, man(nx, ny, ox, oy), nx, ny)
        if best is None or cand < best:
            best = cand

    if best is None:
        return [0, 0]
    nx, ny = best[2], best[3]
    return [nx - sx, ny - sy]