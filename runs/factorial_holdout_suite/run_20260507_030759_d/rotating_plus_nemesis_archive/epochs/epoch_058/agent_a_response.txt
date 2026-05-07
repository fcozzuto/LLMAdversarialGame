def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    resources = observation.get("resources") or []
    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        rx, ry = int(r[0]), int(r[1])
        if not free(rx, ry):
            continue
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer winning the race; then prefer nearer; then lexicographic
        win = ds <= do
        key = (0 if win else 1, ds, -do, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = []
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    pref = [(dx, dy), (dx, 0), (0, dy), (0, 0), (0, 0)]
    for m in pref:
        if m in moves and m not in candidates:
            candidates.append(m)
    for m in moves:
        if m not in candidates:
            candidates.append(m)

    for m in candidates:
        mx, my = m
        nx, ny = sx + mx, sy + my
        if free(nx, ny):
            return [int(mx), int(my)]
    return [0, 0]