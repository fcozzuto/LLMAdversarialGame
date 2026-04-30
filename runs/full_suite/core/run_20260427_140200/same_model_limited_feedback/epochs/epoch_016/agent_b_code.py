def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles_raw = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_raw:
        try:
            obstacles.add((int(p[0]), int(p[1])))
        except Exception:
            pass

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    nearest = None
    bestr = 10**9
    for r in resources:
        try:
            rx, ry = int(r[0]), int(r[1])
        except Exception:
            continue
        d = man(sx, sy, rx, ry)
        if d < bestr:
            bestr = d
            nearest = (rx, ry)

    tx, ty = (w - 1) // 2, (h - 1) // 2
    if nearest is not None:
        tx, ty = nearest

    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        if resources:
            rr_best = 10**9
            for r in resources:
                try:
                    rx, ry = int(r[0]), int(r[1])
                except Exception:
                    continue
                d = man(nx, ny, rx, ry)
                if d < rr_best:
                    rr_best = d
            score = -rr_best * 100 - man(nx, ny, ox, oy)
        else:
            score = -(abs(nx - tx) + abs(ny - ty)) * 10 - man(nx, ny, ox, oy)
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move