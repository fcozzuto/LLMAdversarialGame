def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
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

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not valid(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    def md(ax, ay, bx, by):
        a = ax - bx
        if a < 0:
            a = -a
        b = ay - by
        if b < 0:
            b = -b
        return a + b

    best = None
    best_score = -10**9
    for rx, ry in resources:
        ds = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        score = (do - ds) * 10 - ds
        if score > best_score:
            best_score = score
            best = (rx, ry)

    if best is None:
        stepx = 0 if ox == sx else (1 if ox < sx else -1)
        stepy = 0 if oy == sy else (1 if oy < sy else -1)
        cand = [(-stepx, -stepy), (-stepx, 0), (0, -stepy), (0, 0)]
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    rx, ry = best
    tx = 0 if rx == sx else (1 if rx > sx else -1)
    ty = 0 if ry == sy else (1 if ry > sy else -1)

    for dx, dy in [(tx, ty), (tx, 0), (0, ty), (tx, -ty), (-tx, ty), (0, 0)]:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [dx, dy]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [dx, dy]
    return [0, 0]