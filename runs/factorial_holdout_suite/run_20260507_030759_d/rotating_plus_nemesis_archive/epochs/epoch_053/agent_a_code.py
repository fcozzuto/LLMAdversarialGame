def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    w = int(w)
    h = int(h)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst

    if not res:
        best = (-(10**9), 0, 0)
        for dx, dy in moves[1:]:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                dist = abs(nx - ox) + abs(ny - oy)
                if dist > best[0]:
                    best = (dist, dx, dy)
        if best[1] != 0 or best[2] != 0:
            return [best[1], best[2]]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best_target = res[0]
    best_val = None
    for t in res:
        ds = man((sx, sy), t)
        do = man((ox, oy), t)
        val = (ds - do, ds, -t[0], -t[1])
        if best_val is None or val < best_val:
            best_val = val
            best_target = t

    tx, ty = best_target
    best_move = (10**9, 10**9, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            ds = abs(nx - tx) + abs(ny - ty)
            do = abs(nx - ox) + abs(ny - oy)
            key = (ds, -do, dx, dy)
            if key < best_move:
                best_move = key
    return [best_move[2], best_move[3]]