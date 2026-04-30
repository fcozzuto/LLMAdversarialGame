def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0),  (0, 0),  (1, 0),
            (-1, 1),  (0, 1),  (1, 1)]

    if not resources:
        for dx, dy in [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [dx, dy]
        return [0, 0]

    best_r = None
    best_key = None  # minimize opponent advantage, then prefer closeness
    for r in resources:
        rx, ry = r
        d_me = cheb(sx, sy, rx, ry)
        d_op = cheb(ox, oy, rx, ry)
        key = (- (d_op - d_me), -d_me, rx, ry)  # prefer where we are closer than opponent
        if best_key is None or key > best_key:
            best_key = key
            best_r = r

    tx, ty = best_r
    preferred = []
    step_dx = 0 if tx == sx else (1 if tx > sx else -1)
    step_dy = 0 if ty == sy else (1 if ty > sy else -1)
    preferred.append((step_dx, step_dy))
    if step_dx != 0 and step_dy != 0:
        preferred.extend([(step_dx, 0), (0, step_dy)])

    def move_value(dx, dy):
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            return -10**9
        d_me = cheb(nx, ny, tx, ty)
        d_op = cheb(ox, oy, tx, ty)
        # also softly repel opponent by increasing distance to its current position
        return (d_op - d_me) * 100 - d_me - cheb(nx, ny, ox, oy) * 2

    for dx, dy in preferred:
        if ok(sx + dx, sy + dy):
            return [dx, dy]

    best = (0, 0)
    bestv = -10**9
    # deterministic tie-break by dir order
    for dx, dy in dirs:
        v = move_value(dx, dy)
        if v > bestv:
            bestv = v
            best = (dx, dy)
    if ok(sx + best[0], sy + best[1]):
        return [best[0], best[1]]
    return [0, 0]