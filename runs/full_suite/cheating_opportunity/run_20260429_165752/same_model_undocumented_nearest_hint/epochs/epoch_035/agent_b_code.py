def choose_move(observation):
    W = int(observation.get("grid_width", 8))
    H = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [W - 1, H - 1])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def ok(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    target = None
    if resources:
        target = resources[0]
        bestd = dist((sx, sy), target)
        for t in resources[1:]:
            d = dist((sx, sy), t)
            if d < bestd:
                bestd = d
                target = t

    def score(nx, ny):
        if target is None:
            tx, ty = (W - 1) // 2, (H - 1) // 2
        else:
            tx, ty = target
        s = -dist((nx, ny), (tx, ty))
        s += 0.01 * ((nx - ox) * (nx - ox) + (ny - oy) * (ny - oy))
        return s

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        sc = score(nx, ny)
        if sc > best_score:
            best_score = sc
            best_move = (dx, dy)

    if ok(sx + best_move[0], sy + best_move[1]):
        return [best_move[0], best_move[1]]
    return [0, 0]