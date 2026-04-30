def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    res = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            pos = r.get("pos")
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                res.append((int(pos[0]), int(pos[1])))
            else:
                x = r.get("x")
                y = r.get("y")
                if x is not None and y is not None:
                    res.append((int(x), int(y)))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    candidates = []
    if res:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            nd = 10**9
            for r in res:
                d = dist((nx, ny), r)
                if d < nd:
                    nd = d
            od = 10**9
            for r in res:
                d = dist((ox, oy), r)
                if d < od:
                    od = d
            on_res = any(nx == rx and ny == ry for rx, ry in res)
            candidates.append(((0 if on_res else 1), nd, -dist((nx, ny), (ox, oy)), dx, dy, nd - od))
        candidates.sort()
        return [candidates[0][3], candidates[0][4]]

    best = (10**9, -1, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        oppd = dist((nx, ny), (ox, oy))
        if oppd > best[1] or (oppd == best[1] and dist((nx, ny), (sx, sy)) < best[0]):
            best = (dist((nx, ny), (sx, sy)), oppd, dx, dy)
    return [best[2], best[3]]