def choose_move(observation):
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Pick resource where we have the best "reach advantage"; break ties by closer to self.
    best = None
    best_key = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        takeover = do - ds
        # Encourage grabbing earlier if takeover equal; slightly prefer lower ds.
        key = (takeover, -ds, -cheb(sx, sy, rx, ry) + cheb(ox, oy, rx, ry))
        if best is None or key > best_key:
            best = (rx, ry)
            best_key = key

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Candidate moves (prefer those closer to target; deterministic tie-break).
    candidates = [(-1, -1), (-1, 0), (-1, 1),
                  (0, -1), (0, 0), (0, 1),
                  (1, -1), (1, 0), (1, 1)]
    scored = []
    for mx, my in candidates:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny):
            continue
        dist = cheb(nx, ny, tx, ty)
        # If staying on current cell and already at target, keep still.
        stay_pen = 0 if (mx == 0 and my == 0) else 0
        scored.append((dist, stay_pen, mx, my))

    # If we can step directly toward target without obstacle, do so.
    nx, ny = sx + dx, sy + dy
    if inb(nx, ny):
        return [dx, dy]

    # Otherwise choose best legal move minimizing distance to target.
    if not scored:
        return [0, 0]
    scored.sort(key=lambda t: (t[0], t[1], t[2], t[3]))
    return [int(scored[0][2]), int(scored[0][3])]