def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        best_key = None
        for rx, ry in resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer targets where we are closer than opponent; then closer overall; then deterministic.
            key = (sd - od, sd, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                tx, ty = rx, ry

    txd = tx - sx
    tyd = ty - sy
    stepx = 0
    if txd > 0: stepx = 1
    elif txd < 0: stepx = -1
    stepy = 0
    if tyd > 0: stepy = 1
    elif tyd < 0: stepy = -1

    pref = (stepx, stepy)
    best = None
    best_d = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        # Prefer exact direction, then smaller distance to target, then deterministic move order.
        key = (0 if (dx, dy) == pref else 1, d, dx, dy)
        if best is None or key < best:
            best = key
            best_d = (dx, dy)
    if best_d is None:
        return [0, 0]
    return [best_d[0], best_d[1]]