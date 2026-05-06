def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not res:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if free(nx, ny):
                    return [dx, dy]
        return [0, 0]

    best = None
    for x, y in res:
        sd = man(sx, sy, x, y)
        od = man(ox, oy, x, y)
        key = (sd - od, sd, x, y)  # race resources we are closer to
        if best is None or key < best[0]:
            best = (key, (x, y))
    tx, ty = best[1]

    best_step = (10**9, 0, 0)
    # tie-break deterministically to reduce behavioral distance
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            # prefer moves that reduce our distance to target, and also shrink opponent's distance to it
            ns = man(nx, ny, tx, ty)
            no = man(ox, oy, tx, ty)
            key = (ns, no, dx, dy, nx, ny)
            if key < best_step:
                best_step = key
                best_move = [dx, dy]
    return best_move