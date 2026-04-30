def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if r and len(r) == 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        best = (0, 0)
        bestv = -10**9
        d0 = cheb(sx, sy, ox, oy)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny): 
                continue
            dn = cheb(nx, ny, ox, oy)
            v = (dn - d0) * 40 - dn * 2
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    def score_from(px, py):
        bestr = -10**18
        for rx, ry in resources:
            md = cheb(px, py, rx, ry)
            od = cheb(ox, oy, rx, ry)
            if md == 0:
                vr = 100000
            else:
                vr = (od - md) * 30 + (1.0 / (md + 1)) * 80
                if od <= md:
                    vr -= 18  # avoid races I'm unlikely to win
            if vr > bestr:
                bestr = vr
        return bestr

    d0 = cheb(sx, sy, ox, oy)
    best = (0, 0)
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        dn = cheb(nx, ny, ox, oy)
        base = score_from(nx, ny)
        # strategic change: actively avoid closing on opponent unless it improves resource advantage
        risk = (d0 - dn) * 25  # positive if we get closer (bad)
        v = base - risk - dn * 1.5 + (dn - d0) * 8
        if v > bestv:
            bestv = v
            best = (dx, dy)
    return [best[0], best[1]]