def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = []
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.append((x, y))
    obstacles_set = set(obstacles)

    resources = []
    for p in (observation.get("resources") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles_set:
                resources.append((x, y))

    if not inb(sx, sy) or (sx, sy) in obstacles_set or not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    obs_adj = set()
    for ax, ay in obstacles:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = ax + dx, ay + dy
                if inb(nx, ny):
                    obs_adj.add((nx, ny))
    obs_adj.discard(list(obstacles_set)[0]) if obstacles_set else None

    cx, cy = w // 2, h // 2

    def eval_pos(nx, ny):
        if (nx, ny) in obstacles_set:
            return -10**9
        dcenter = man(nx, ny, cx, cy)
        proximity_pen = 0
        if (nx, ny) in obs_adj:
            proximity_pen += 2
        best_adv = -10**9
        best_my = 10**9
        for rx, ry in resources:
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            adv = opd - myd  # positive if we are closer
            if adv > best_adv:
                best_adv = adv
            if myd < best_my:
                best_my = myd
        # Prefer being closer than opponent; if tied/behind, prefer reducing our own distance.
        return best_adv * 3 - best_my - dcenter * 0.1 - proximity_pen * 1.5

    best = (0, 0)
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        v = eval_pos(nx, ny)
        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]