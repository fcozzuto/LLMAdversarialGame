def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (w - 1, h - 1)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def dist(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        tx = cx if sx < cx else (-1 if sx > cx else 0)
        ty = cy if sy < cy else (-1 if sy > cy else 0)
        dx = 0 if sx == cx else (1 if sx < cx else -1)
        dy = 0 if sy == cy else (1 if sy < cy else -1)
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            return [dx, dy]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    best = None
    bestv = None
    for rx, ry in resources:
        ds = dist(sx, sy, rx, ry)
        do = dist(ox, oy, rx, ry)
        v = ds - 0.75 * do
        if bestv is None or v < bestv or (v == bestv and ds < best[2]):
            bestv = v
            best = (rx, ry, ds)

    tx, ty = best[0], best[1]
    dx = 0 if sx == tx else (1 if sx < tx else -1)
    dy = 0 if sy == ty else (1 if sy < ty else -1)

    preferred = [(dx, dy), (dx, 0), (0, dy), (-dx, dy), (dx, -dy), (0, 0)]
    tried = set()

    for cand in preferred + moves:
        cx, cy = cand
        if (cx, cy) in tried:
            continue
        tried.add((cx, cy))
        nx, ny = sx + cx, sy + cy
        if ok(nx, ny):
            return [int(cx), int(cy)]

    return [0, 0]