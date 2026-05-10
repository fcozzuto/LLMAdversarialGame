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
        # Prefer resources we can reach at least as fast as opponent; otherwise still pick best advantage.
        adv = do - ds
        # Secondary: nearer to us; tertiary: prefer staying away from edges (minor tie-break).
        edge_pen = abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2)
        key = (adv, -ds, -edge_pen)
        if best is None or key > best[0]:
            best = (key, rx, ry)

    if best is None:
        return [0, 0]

    _, tx, ty = best
    def sgn(v):
        return 1 if v > 0 else (-1 if v < 0 else 0)

    dx = sgn(tx - sx)
    dy = sgn(ty - sy)

    candidates = [
        (dx, dy),
        (dx, 0),
        (0, dy),
        (dx, -dy),
        (-dx, dy),
        (-dx, 0),
        (0, -dy),
        (-dx, -dy),
        (0, 0),
    ]
    for mx, my in candidates:
        nx, ny = sx + mx, sy + my
        if ok(nx, ny):
            return [int(mx), int(my)]
    return [0, 0]