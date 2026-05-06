def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sp = observation.get("self_position", (0, 0))
    op = observation.get("opponent_position", (0, 0))
    sx, sy = sp if isinstance(sp, (list, tuple)) and len(sp) >= 2 else (0, 0)
    ox, oy = op if isinstance(op, (list, tuple)) and len(op) >= 2 else (0, 0)

    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int):
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    resources = observation.get("resources", []) or []
    rpos = []
    for r in resources:
        if isinstance(r, dict):
            q = r.get("position")
        else:
            q = r
        if isinstance(q, (list, tuple)) and len(q) >= 2:
            x, y = q[0], q[1]
            if isinstance(x, int) and isinstance(y, int) and inb(x, y) and (x, y) not in blocked:
                rpos.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not rpos:
        best = (10**9, 0, (0, 0))
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in blocked:
                continue
            d = abs(nx - ox) + abs(ny - oy)
            cand = (d, 0, (dx, dy))
            if cand < best:
                best = cand
        return list(best[2])

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    best = (10**9, 10**9, 0, (0, 0))
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        myd = min(dist((nx, ny), r) for r in rpos)
        od = min(dist((ox, oy), r) for r in rpos) if rpos else 0
        gain = myd - od
        cand = (myd, gain, (dx == 0 and dy == 0), (dx, dy))
        if cand < best:
            best = cand
    return list(best[3])