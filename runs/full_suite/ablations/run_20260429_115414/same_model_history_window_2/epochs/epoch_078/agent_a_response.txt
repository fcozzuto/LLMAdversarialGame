def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    if w <= 0: w = 8
    if h <= 0: h = 8

    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                resources.append((rx, ry))

    if not resources:
        resources = [(w // 2, h // 2)]

    def dist(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    best = None
    best_score = None
    for dx, dy, nx, ny in moves:
        # Score: try to secure a resource where we gain distance advantage,
        # penalize risky moves by preferring nearer-to-best targets deterministically.
        local_best = None
        for rx, ry in resources:
            sd = dist(nx, ny, rx, ry)
            od = dist(ox, oy, rx, ry)
            # Strong preference for winning nearby targets; if tie, choose smaller sd then smaller rx/ry.
            score = (od - sd, -sd, -rx, -ry)
            if local_best is None or score > local_best:
                local_best = score
        if best is None or local_best > best_score:
            best_score = local_best
            best = (dx, dy)

    return [int(best[0]), int(best[1])]