def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    if resources:
        best_overall = None
        best_move = None
        for dx, dy, nx, ny in cand:
            mydists = []
            for rx, ry in resources:
                myd = man(nx, ny, rx, ry)
                opd = man(ox, oy, rx, ry)
                adv = opd - myd
                mydists.append((adv, -myd, rx, ry))
            mydists.sort(reverse=True)
            adv, negd, _, _ = mydists[0]
            if best_overall is None or (adv, negd) > best_overall:
                best_overall = (adv, negd)
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None
    best_move = None
    for dx, dy, nx, ny in cand:
        # deterministic center-seeking if no resources
        dist2 = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
        if best is None or dist2 < best:
            best = dist2
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]