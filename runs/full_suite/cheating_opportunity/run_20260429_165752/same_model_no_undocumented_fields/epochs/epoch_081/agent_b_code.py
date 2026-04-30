def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obs = observation.get("obstacles") or []
    obstacles = set()
    for p in obs:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    res = observation.get("resources") or []
    resources = []
    for p in res:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        d = x1 - x2
        if d < 0:
            d = -d
        e = y1 - y2
        if e < 0:
            e = -e
        return d + e

    candidates = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = [(dx, dy) for dx, dy in candidates if inb(sx + dx, sy + dy) and (sx + dx, sy + dy) not in obstacles]
    if not candidates:
        return [0, 0]

    if resources:
        best_t = None
        best_adv = -10**18
        for rx, ry in resources:
            ds = md(sx, sy, rx, ry)
            do = md(ox, oy, rx, ry)
            adv = (do - ds)  # positive means we are closer
            if adv > best_adv or (adv == best_adv and (ds < (md(sx, sy, best_t[0], best_t[1]) if best_t else 10**9))):
                best_adv = adv
                best_t = (rx, ry)
        rx, ry = best_t
        best = None
        best_val = -10**18
        for dx, dy in candidates:
            nx, ny = sx + dx, sy + dy
            ds = md(nx, ny, rx, ry)
            do = md(ox, oy, rx, ry)
            val = (do - ds, -ds, -(abs(nx - rx) + abs(ny - ry)))
            if best is None or val > best_val:
                best = (dx, dy)
                best_val = val
        return [best[0], best[1]]

    # No resources: move toward center while not getting closer to opponent too fast
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best = None
    best_val = -10**18
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        to_center = md(nx, ny, cx, cy)
        to_opp = md(nx, ny, ox, oy)
        val = (to_opp - md(sx, sy, ox, oy), -to_center, to_opp)
        if best is None or val > best_val:
            best = (dx, dy)
            best_val = val
    return [best[0], best[1]]