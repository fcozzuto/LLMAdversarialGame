def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    ap = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(ap[0]), int(ap[1])

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            x, y = int(o[0]), int(o[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    # Pick resources where we beat opponent on distance; maximize margin, then minimize our distance.
    best = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        margin = do - ds  # positive => we are closer
        key = (-margin, ds, rx, ry)
        if best is None or key < best[0]:
            best = (key, rx, ry)
    _, tx, ty = best

    # Greedy step toward target with obstacle avoidance; deterministic tie-break by move order.
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def ok(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    curd = cheb(sx, sy, tx, ty)
    bestm = None
    bestk = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        nd = cheb(nx, ny, tx, ty)
        k = (-(nd < curd), nd, dx, dy)  # prefer decreasing, then smaller distance, then deterministic
        if bestk is None or k < bestk:
            bestk = k
            bestm = (dx, dy)
    if bestm is None:
        return [0, 0]
    return [int(bestm[0]), int(bestm[1])]