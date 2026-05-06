def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h and (x, y) not in obs
    def man(a, b, c, d): return abs(a - c) + abs(b - d)

    def opp_step(cx, cy):
        best = None
        br = None
        for rx, ry in res:
            d = man(cx, cy, rx, ry)
            if best is None or d < best:
                best, br = d, (rx, ry)
        tx, ty = br
        bestm = (0, 0)
        bestv = None
        for dx, dy in moves:
            nx, ny = cx + dx, cy + dy
            if not inb(nx, ny):
                continue
            v = man(nx, ny, tx, ty)
            if bestv is None or v < bestv:
                bestv = v
                bestm = (dx, dy)
        return bestm

    best_move = (0, 0)
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        odx, ody = opp_step(ox, oy)
        nox, noy = ox + odx, oy + ody

        val = None
        for rx, ry in res:
            myd = man(nx, ny, rx, ry)
            opd = man(nox, noy, rx, ry)
            # Favor resources where we are closer; penalize if opponent keeps the lead.
            v = (opd - myd) * 100 - myd
            if val is None or v > val:
                val = v
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]