def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inside(x, y):
        return 0 <= x < int(w) and 0 <= y < int(h)

    blocked = set()
    for p in (observation.get("obstacles", None) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            px, py = int(p[0]), int(p[1])
            if inside(px, py):
                blocked.add((px, py))

    resources = []
    for r in (observation.get("resources", None) or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if inside(rx, ry) and (rx, ry) not in blocked:
                resources.append((rx, ry))

    if resources:
        def md(x1, y1, x2, y2):
            d = x1 - x2
            if d < 0: d = -d
            e = y1 - y2
            if e < 0: e = -e
            return d + e
        target = min(resources, key=lambda t: (md(t[0], t[1], ox, oy), t[0], t[1]))
    else:
        target = (ox, oy)

    moves = [(-1, 0), (0, -1), (1, 0), (0, 1), (0, 0)]
    def md(x1, y1, x2, y2):
        d = x1 - x2
        if d < 0: d = -d
        e = y1 - y2
        if e < 0: e = -e
        return d + e

    best = None
    best_d = 10**18
    tx, ty = target
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in blocked:
            continue
        d = md(nx, ny, tx, ty)
        if d < best_d:
            best_d = d
            best = [dx, dy]
    if best is None:
        return [0, 0]
    return best