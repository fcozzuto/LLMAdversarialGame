def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = observation.get("obstacles") or []
    obstacles = set()
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not valid(sx, sy):
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    def dist(a, b, x, y):
        d1 = a - x
        if d1 < 0: d1 = -d1
        d2 = b - y
        if d2 < 0: d2 = -d2
        return d1 + d2

    target = None
    if resources:
        tx, ty = resources[0]
        best = dist(sx, sy, tx, ty)
        for x, y in resources[1:]:
            d = dist(sx, sy, x, y)
            if d < best:
                best, tx, ty = d, x, y
        target = (tx, ty)
    else:
        target = (ox, oy)

    best_move = [0, 0]
    best_score = 10**9
    tx, ty = target

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = dist(nx, ny, tx, ty)
        cur = dist(sx, sy, tx, ty)
        score = nd + (1 if (dx, dy) != (0, 0) and nd >= cur else 0)
        if nd < cur and score < best_score:
            best_score = score
            best_move = [dx, dy]

    if best_move == [0, 0]:
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            nd = dist(nx, ny, tx, ty)
            score = nd
            if score < best_score:
                best_score = score
                best_move = [dx, dy]

    return best_move