def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    try:
        w = int(w)
        h = int(h)
    except:
        w = 8
        h = 8
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    resources = observation.get("resources") or []
    res_pos = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                res_pos.append((rx, ry))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = lambda x, y: 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    if (sx, sy) == (ox, oy):
        return [0, 0]

    best = None
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        cur = (nx, ny)
        oppd = man(cur, (ox, oy))
        if res_pos:
            mind = 10**9
            for rp in res_pos:
                d = man(cur, rp)
                if d < mind:
                    mind = d
        else:
            mind = 0
        val = oppd * -2
        val += mind * -1
        if (nx, ny) == (ox, oy):
            val -= 10**6
        if best is None or val > best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]