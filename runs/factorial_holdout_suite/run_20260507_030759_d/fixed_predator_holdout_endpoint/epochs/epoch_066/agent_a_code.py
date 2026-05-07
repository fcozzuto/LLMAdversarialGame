def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    targets = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            tx, ty = int(r[0]), int(r[1])
            if ok(tx, ty):
                targets.append((tx, ty))
    if not targets:
        tx, ty = w // 2, h // 2
        targets = [(tx, ty)]

    best = None
    for dx, dy in dirs:
        nx, ny = int(sx) + dx, int(sy) + dy
        if not ok(nx, ny):
            continue
        myd = 10 * dist((nx, ny), (ox, oy))
        score = -myd
        best_tie = 0
        for tx, ty in targets[:8]:
            sd = dist((nx, ny), (tx, ty))
            od = dist((ox, oy), (tx, ty))
            win = (od - sd)
            score = max(score, 1000 * (win >= 2) + 100 * (win > 0) - sd)
            t = -(tx * 1000 + ty)
            if sd < 10**9:
                best_tie = max(best_tie, -sd + t)
        key = (score, -dist((nx, ny), (targets[0][0], targets[0][1])), -(dx + dy * 2))
        if best is None or key > best[0]:
            best = (key, [dx, dy])

    return best[1] if best is not None else [0, 0]