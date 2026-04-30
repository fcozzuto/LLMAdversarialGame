def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not (0 <= sx < w and 0 <= sy < h) or not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def step_towards(tx, ty):
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        candidates = [(dx, dy), (dx, 0), (0, dy), (-dx, dy), (dx, -dy), (-dx, 0), (0, -dy), (0, 0)]
        # Deduplicate while preserving order
        seen = set()
        out = []
        for c in candidates:
            if c not in seen:
                seen.add(c)
                out.append(c)
        return out

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best_target = None
    best_metric = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Primary: maximize our advantage (do - ds). Secondary: be closer (smaller ds).
        metric = (do - ds, -ds, rx, ry)
        if best_metric is None or metric > best_metric:
            best_metric = metric
            best_target = (rx, ry)

    rx, ry = best_target
    # If we are not actually closer than opponent, prefer nearest anyway (material strategy shift vs last epochs).
    ds = cheb(sx, sy, rx, ry)
    do = cheb(ox, oy, rx, ry)
    if do <= ds:
        nearest = None
        nd = None
        for r2x, r2y in resources:
            d2 = cheb(sx, sy, r2x, r2y)
            if nd is None or d2 < nd or (d2 == nd and (r2x, r2y) < nearest):
                nd = d2
                nearest = (r2x, r2y)
        rx, ry = nearest

    for dx, dy in step_towards(rx, ry):
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            return [int(dx), int(dy)]
    return [0, 0]