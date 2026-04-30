def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                resources.append((rx, ry))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    cx, cy = (w - 1) // 2, (h - 1) // 2
    target = None

    if resources:
        best_key = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            key = (ds - do, ds, -rx, -ry)  # prefer where we're relatively closer; deterministic tie-break
            if best_key is None or key < best_key:
                best_key = key
                target = (rx, ry)
    else:
        target = (cx, cy)

    tx, ty = target
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ds2 = cheb(nx, ny, tx, ty)
        do2 = cheb(nx, ny, ox, oy)
        cur_sep = cheb(sx, sy, ox, oy)
        # Prefer reducing distance to target; if tied, prefer moves that also increase separation from opponent
        key = (ds2, -do2, -(cur_sep > 0 and cur_sep))
        if best is None or key < best[0]:
            best = (key, (dx, dy))

    if best is None:
        return [0, 0]
    dx, dy = best[1]
    return [int(dx), int(dy)]