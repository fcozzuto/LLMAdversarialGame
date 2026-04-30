def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    moves = []
    for i, (dx, dy) in enumerate(deltas):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obs:
            continue
        # obstacle "risk": how many adjacent obstacle cells
        risk = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                tx, ty = nx + ax, ny + ay
                if inb(tx, ty) and (tx, ty) in obs:
                    risk += 1
        # Choose resource target with best advantage over opponent
        best = None
        for rx, ry in res:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # prefer getting a resource closer than opponent; small bonus for nearer resources overall
            gain = (opd - myd) * 10 - myd
            # deterministic tiny tie-break: prefer lower x then y among equal gain
            tieb = rx * 9 + ry
            score = gain * 100000 - tieb
            if best is None or score > best[0]:
                best = (score, rx, ry)
        # add slight preference to move generally toward opponent-blocking direction (toward opposite corner)
        # opposite corner is (7,7) if we are (0,0)-side, else (0,0); use cheb to it
        tx, ty = (w - 1, h - 1) if (sx + sy) <= (w - 1 - sx + h - 1 - sy) else (0, 0)
        toward = -cheb(nx, ny, tx, ty)
        total = best[0] + toward - risk
        moves.append((total, i, dx, dy))
    if not moves:
        return [0, 0]
    moves.sort(reverse=True)
    return [int(moves[0][2]), int(moves[0][3])]