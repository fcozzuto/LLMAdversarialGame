def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb_dist(a, b):
        dx = a[0] - b[0]
        if dx < 0:
            dx = -dx
        dy = a[1] - b[1]
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best = None
    best_val = None
    for r in res:
        st = cheb_dist((sx, sy), r)
        ot = cheb_dist((ox, oy), r)
        can_take = 1 if st <= ot else 0
        # Primary: we can take first; Secondary: maximize time advantage; Tertiary: closer to us
        val = (can_take, ot - st, -st)
        if best_val is None or val > best_val:
            best_val = val
            best = r

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    # Try diagonal first; if blocked, try orthogonal; else stay.
    cand = []
    nx, ny = sx + dx, sy + dy
    cand.append((dx, dy))
    cand.append((dx, 0))
    cand.append((0, dy))
    cand.append((0, 0))
    for ddx, ddy in cand:
        x, y = sx + ddx, sy + ddy
        if inb(x, y) and (x, y) not in obs:
            return [int(ddx), int(ddy)]
    return [0, 0]