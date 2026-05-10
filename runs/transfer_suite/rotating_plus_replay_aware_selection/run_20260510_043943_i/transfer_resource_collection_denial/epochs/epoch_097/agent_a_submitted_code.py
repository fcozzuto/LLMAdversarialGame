def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def best_target():
        best = None
        for r in resources:
            if not (isinstance(r, (list, tuple)) and len(r) >= 2):
                continue
            rx, ry = r[0], r[1]
            if not ok(rx, ry):
                continue
            ds = man(sx, sy, rx, ry)
            do = man(ox, oy, rx, ry)
            cand = (do - ds, -ds, rx, ry)
            if best is None or cand > best:
                best = cand
        return None if best is None else best[2], best[3]

    tgt = best_target()
    if not tgt:
        return [0, 0]
    tx, ty = tgt

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = None
    bestd = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = man(nx, ny, tx, ty)
        cand = (d, man(nx, ny, ox, oy), dx, dy)
        if bestm is None or cand < bestm:
            bestm = cand
            bestd = d
    if bestm is None:
        return [0, 0]
    return [bestm[2], bestm[3]]