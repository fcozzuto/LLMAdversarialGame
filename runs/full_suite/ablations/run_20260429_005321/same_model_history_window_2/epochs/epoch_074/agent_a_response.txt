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
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        for dx, dy in dirs:
            if ok(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    best_t = resources[0]
    best_s = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prefer resources where we are closer; else fall back to closest resource.
        score = (opd - myd) * 1000 - myd
        if best_s is None or score > best_s or (score == best_s and (rx, ry) < best_t):
            best_s = score
            best_t = (rx, ry)

    rx, ry = best_t
    best_m = (0, 0, -10**18)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        myd2 = cheb(nx, ny, rx, ry)
        opd_now = cheb(ox, oy, rx, ry)
        # Deterministic tie-break by fixed dirs order via score comparisons only.
        score2 = (opd_now - myd2) * 1000 - myd2
        if score2 > best_m[2]:
            best_m = (dx, dy, score2)

    return [int(best_m[0]), int(best_m[1])]