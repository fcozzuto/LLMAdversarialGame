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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if ok(x, y):
                resources.append((x, y))

    if not ok(sx, sy):
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    legal = [(dx, dy) for dx, dy in dirs if ok(sx + dx, sy + dy)]
    if not legal:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    cx, cy = (w - 1) // 2, (h - 1) // 2

    best = None
    bestv = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        # If on a resource: strong bias to stay/collect.
        v = 0
        for (rx, ry) in resources:
            if nx == rx and ny == ry:
                v += 10**6
        # Otherwise, compete for resources: prefer resources where we are closer than opponent.
        for (rx, ry) in resources:
            d1 = cheb(nx, ny, rx, ry)
            d2 = cheb(ox, oy, rx, ry)
            # closeness advantage + slight preference for nearer absolute distance.
            v += (d2 - d1) * 2000 - d1
        # If few resources remain, bias toward center to reduce travel times.
        if (observation.get("remaining_resource_count") or 0) <= 4:
            v += -cheb(nx, ny, cx, cy) * 20
        # Deterministic tie-breaker: smaller dx, then smaller dy.
        if best is None or v > bestv or (v == bestv and (dx, dy) < best):
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]