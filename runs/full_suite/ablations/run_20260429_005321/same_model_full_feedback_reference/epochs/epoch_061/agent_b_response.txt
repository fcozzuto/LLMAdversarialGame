def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best, bestv = (0, 0), -10**30
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            v = -d2(nx, ny, cx, cy) - 0.25 * d2(nx, ny, ox, oy)
            if v > bestv:
                bestv, best = v, [dx, dy]
        return best

    best, bestv = [0, 0], -10**60
    res_sorted = sorted(resources, key=lambda r: d2(sx, sy, r[0], r[1]))
    top = res_sorted[:5] if len(res_sorted) > 5 else res_sorted

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        v = 0.0
        for i, (rx, ry) in enumerate(top):
            ds = d2(nx, ny, rx, ry)
            do = d2(ox, oy, rx, ry)
            adv = (do - ds)
            v += adv * (1.4 - 0.15 * i)
        # Small tie-break: avoid moving closer to opponent while we're not improving advantage.
        v -= 0.06 * d2(nx, ny, ox, oy)
        if v > bestv:
            bestv, best = v, [dx, dy]
    return best