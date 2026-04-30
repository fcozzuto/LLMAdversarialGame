def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                resources.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def md(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a + b

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1), (0, 0)]
    best_move = (0, 0)
    best_val = -10**18

    if resources:
        nearest = min(resources, key=lambda r: md(sx, sy, r[0], r[1]))
        tx, ty = nearest
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            val = -md(nx, ny, tx, ty)
            if (nx, ny) in resources:
                val += 10**6
            if md(nx, ny, ox, oy) <= 1:
                val -= 5
            if val > best_val:
                best_val, best_move = val, (dx, dy)
    else:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            val = -md(nx, ny, cx, cy)
            val += md(nx, ny, ox, oy) * 2
            if val > best_val:
                best_val, best_move = val, (dx, dy)

    return [int(best_move[0]), int(best_move[1])]