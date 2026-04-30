def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if ok(rx, ry):
                resources.append((rx, ry))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if ok(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not resources:
        best = None
        best_move = (0, 0)
        for dx, dy, nx, ny in legal:
            key = (cheb(nx, ny, ox, oy), dx, dy)
            if best is None or key < best:
                best = key
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    # Choose a small deterministic set of closest resources as targets.
    scored_res = []
    for rx, ry in resources:
        scored_res.append((cheb(sx, sy, rx, ry), rx, ry))
    scored_res.sort(key=lambda t: (t[0], t[1], t[2]))
    targets = [(t[1], t[2]) for t in scored_res[:4]]  # up to 4

    best_key = None
    best_move = (0, 0)
    for dx, dy, nx, ny in legal:
        best_d = None
        for tx, ty in targets:
            d = cheb(nx, ny, tx, ty)
            if best_d is None or d < best_d:
                best_d = d
        # Primary: minimize distance to best target
        # Secondary: maximize distance from opponent (avoid contesting)
        # Tertiary: deterministic tie-break toward smaller dx, then dy.
        dist_op = cheb(nx, ny, ox, oy)
        key = (best_d, -dist_op, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]