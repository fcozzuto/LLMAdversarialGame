def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            resources.append((int(r[0]), int(r[1])))
        elif isinstance(r, dict):
            pos = r.get("pos", None)
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                resources.append((int(pos[0]), int(pos[1])))
            else:
                x = r.get("x", None)
                y = r.get("y", None)
                if x is not None and y is not None:
                    resources.append((int(x), int(y)))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(a, b):
        dx = a[0] - b[0]
        if dx < 0:
            dx = -dx
        dy = a[1] - b[1]
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    neighbors = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    target = None
    if resources:
        bestd = None
        for t in resources:
            d = dist((sx, sy), t)
            if bestd is None or d < bestd or (d == bestd and (t[0], t[1]) < target):
                bestd = d
                target = t
    if target is None:
        target = (w // 2, h // 2)

    best = None
    bestscore = None
    for dx, dy in neighbors:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        nd = dist((nx, ny), target)
        od = dist((nx, ny), (ox, oy))
        score = nd * 10 + od
        if bestscore is None or score < bestscore or (score == bestscore and (dx, dy) < best):
            bestscore = score
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [best[0], best[1]]