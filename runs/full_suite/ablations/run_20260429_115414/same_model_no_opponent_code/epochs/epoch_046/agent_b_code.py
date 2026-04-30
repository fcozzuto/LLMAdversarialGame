def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    cx, cy = (w - 1) // 2, (h - 1) // 2
    best = None
    best_score = -10**18

    targets = resources
    if not targets:
        targets = [(cx, cy)]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Favor reducing distance to closest resource; penalize letting opponent be closer.
        best_t = None
        for tx, ty in targets:
            myd = dist(nx, ny, tx, ty)
            opd = dist(ox, oy, tx, ty)
            score = (opd - myd) * 100 - myd - dist(nx, ny, cx, cy) * 2
            if best_t is None or score > best_score:
                best_t = (score, tx, ty)
        if best_t is None:
            score = dist(nx, ny, cx, cy) * -1
        else:
            score = best_t[0]

        # Small deterministic tiebreaker: prefer moves with smaller dx, then dy.
        score2 = score - (dx + 1) * 0.01 - (dy + 1) * 0.001
        if score2 > best_score:
            best_score = score2
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best