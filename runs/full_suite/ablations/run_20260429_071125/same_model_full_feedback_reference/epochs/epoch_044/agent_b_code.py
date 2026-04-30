def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not ok(sx, sy):
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                return [int(dx), int(dy)]
        return [0, 0]

    if not resources:
        # Drift away from opponent to reduce contention
        best = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny): 
                continue
            d = cheb(nx, ny, ox, oy)
            if best is None or d > best[0]:
                best = (d, dx, dy)
        return [int(best[1]), int(best[2])] if best else [0, 0]

    def value_at(px, py):
        bestv = -10**18
        for rx, ry in resources:
            myd = cheb(px, py, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Prefer resources where we are (or become) closer than opponent
            v = (opd - myd) * 20 - myd
            if v > bestv:
                bestv = v
        return bestv

    best = None
    base = value_at(sx, sy)
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        v = value_at(nx, ny)
        # Small tie-break toward immediate progress
        if best is None or v > best[0] or (v == best[0] and cheb(nx, ny, ox, oy) < best[2]):
            best = (v, dx, dy, cheb(nx, ny, ox, oy))

    if best and best[0] >= base - 1:
        return [int(best[1]), int(best[2])]
    return [0, 0]