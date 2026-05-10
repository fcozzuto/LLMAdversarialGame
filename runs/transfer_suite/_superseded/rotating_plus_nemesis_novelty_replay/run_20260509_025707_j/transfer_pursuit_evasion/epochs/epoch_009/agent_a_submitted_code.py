def choose_move(observation):
    w = observation.get("grid_width", 0) or 0
    h = observation.get("grid_height", 0) or 0
    w = int(w)
    h = int(h)
    if w <= 0 or h <= 0:
        return [0, 0]

    def getp(key):
        p = observation.get(key)
        if not p or len(p) < 2:
            return None
        try:
            return int(p[0]), int(p[1])
        except Exception:
            return None

    sp = getp("self_position")
    op = getp("opponent_position")
    if sp is None:
        return [0, 0]
    sx, sy = sp
    ox, oy = op if op is not None else (sx, sy)

    obstacles = set()
    for o in observation.get("obstacles") or []:
        q = getp(o) if isinstance(o, (list, tuple)) else None
        if q is None:
            continue
        obstacles.add((q[0], q[1]))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            try:
                rx, ry = int(r[0]), int(r[1])
                res.append((rx, ry))
            except Exception:
                pass

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def d2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    best = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        if res:
            md = None
            for rx, ry in res:
                dd = d2(nx, ny, rx, ry)
                if md is None or dd < md:
                    md = dd
            if md is None:
                md = 10**18
            score_primary = -md
        else:
            score_primary = d2(nx, ny, ox, oy)  # go away if no resources

        # Prefer moves that keep options open (more free neighbors), deterministic tie-break by dx,dy
        free = 0
        for ddx, ddy in moves:
            tx, ty = nx + ddx, ny + ddy
            if ok(tx, ty):
                free += 1
        score_secondary = free

        key = (score_primary, score_secondary, -abs(dx) - abs(dy), -dx, -dy)
        if best is None or key > best:
            best = key
            best_move = [dx, dy]

    return best_move