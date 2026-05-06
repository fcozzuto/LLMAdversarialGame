def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (sx, sy))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    def to_xy(p):
        try:
            if isinstance(p, dict):
                x = p.get("x", p.get("X", p.get("col", p.get("cx", 0))))
                y = p.get("y", p.get("Y", p.get("row", p.get("cy", 0))))
            else:
                x, y = p[0], p[1]
            x, y = int(x), int(y)
            if 0 <= x < w and 0 <= y < h:
                return (x, y)
        except Exception:
            pass
        return None

    resources = []
    for r in observation.get("resources", []) or []:
        rp = to_xy(r)
        if rp is not None:
            resources.append(rp)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        op = to_xy(o)
        if op is not None:
            obstacles.add(op)

    try:
        sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    except Exception:
        sx = sy = ox = oy = 0

    def manh(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if not resources:
        return [0, 0]

    best_val = None
    target = resources[0]
    for t in resources:
        sd = manh((sx, sy), t)
        od = manh((ox, oy), t)
        v = (od - sd) * 10 - sd  # prefer where we are closer, and closer overall
        if best_val is None or v > best_val:
            best_val, target = v, t

    tx, ty = target
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def obst_pen(x, y):
        if (x, y) in obstacles:
            return 1000
        p = 0
        for (ox2, oy2) in obstacles:
            d = abs(ox2 - x) + abs(oy2 - y)
            if d == 0:
                p += 1000
            else:
                p += max(0, 3 - d) * 3  # stay away from obstacles
        return p

    best_score = None
    best_move = [0, 0]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        sd2 = manh((nx, ny), (tx, ty))
        # discourage letting opponent get too near the same target
        od2 = manh((ox, oy), (tx, ty))
        # slight bias toward progressing while not overcommitting
        score = (od2 - sd2) * 10 - sd2 - obst_pen(nx, ny)
        if best_score is None or score > best_score:
            best_score, best_move = score, [dx, dy]

    return best_move