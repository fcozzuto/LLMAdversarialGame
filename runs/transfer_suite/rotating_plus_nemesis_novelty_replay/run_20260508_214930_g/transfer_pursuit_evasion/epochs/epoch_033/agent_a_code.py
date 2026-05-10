def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for b in obstacles:
        if isinstance(b, (list, tuple)) and len(b) >= 2 and b[0] is not None and b[1] is not None:
            obs.add((int(b[0]), int(b[1])))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2 and r[0] is not None and r[1] is not None:
            res.append((int(r[0]), int(r[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def d2(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        return dx * dx + dy * dy

    def obs_pen(x, y):
        if (x, y) in obs:
            return 100000
        p = 0
        for ddx in (-1, 0, 1):
            for ddy in (-1, 0, 1):
                if ddx or ddy:
                    if (x + ddx, y + ddy) in obs:
                        p += 20
        return p

    best = None
    bestv = -10**18
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            v = -obs_pen(nx, ny)
            if res:
                md = None
                for rx, ry in res:
                    dd = d2(nx, ny, rx, ry)
                    if md is None or dd < md:
                        md = dd
                v += -md
            v += d2(nx, ny, ox, oy) // 4
            if v > bestv:
                bestv = v
                best = [dx, dy]
    return best if best is not None else [0, 0]