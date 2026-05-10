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

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    best = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        rx, ry = r[0], r[1]
        if not ok(rx, ry):
            continue
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # Prefer resources we can secure: maximize (do - ds), then minimize ds.
        # If opponent can't reach, do is large so (do-ds) helps.
        pri = (do - ds, -ds)
        if best is None or pri > best[0]:
            best = (pri, rx, ry)
    if best is None:
        return [0, 0]

    _, tx, ty = best
    # Build candidate moves (prefer diagonal that reduces distance most).
    cand = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    bestm = None
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        nds = man(nx, ny, tx, ty)
        ndo = man(ox, oy, tx, ty)
        # Lower our distance; also prefer moves that don't reduce our advantage.
        val = (-nds, -abs((ndo - nds)), -man(nx, ny, ox, oy))
        if bestm is None or val > bestm[0]:
            bestm = (val, dx, dy)
    if bestm is None:
        return [0, 0]
    return [int(bestm[1]), int(bestm[2])]