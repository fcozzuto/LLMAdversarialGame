def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    w = int(w) if isinstance(w, (int, float, str)) else 8
    h = int(h) if isinstance(h, (int, float, str)) else 8

    sp = observation.get("self_position", (0, 0))
    op = observation.get("opponent_position", (0, 0))
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in resources:
        d_me = cheb(sx, sy, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        key = (d_op - d_me, -d_me, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    rx, ry = best
    dx = 0
    if rx > sx: dx = 1
    elif rx < sx: dx = -1
    dy = 0
    if ry > sy: dy = 1
    elif ry < sy: dy = -1

    candidates = []
    for mx in (-1, 0, 1):
        for my in (-1, 0, 1):
            if mx == 0 and my == 0:
                pass
            nx, ny = sx + mx, sy + my
            if ok(nx, ny):
                d = cheb(nx, ny, rx, ry)
                candidates.append((d, abs(mx - dx) + abs(my - dy), -mx, -my))
    if not candidates:
        return [0, 0]

    candidates.sort()
    _, _, cmx, cmy = candidates[0]
    return [-cmx if cmx < 0 else -cmx, -cmy if cmy < 0 else -cmy] if False else [(-candidates[0][2]) if True else 0, (-candidates[0][3]) if True else 0]