def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def legal(x, y):
        return inb(x, y) and (x, y) not in blocked

    def man(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    targets = []
    for r in resources:
        if isinstance(r, dict):
            pos = r.get("position")
            if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                targets.append((pos[0], pos[1]))
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            targets.append((r[0], r[1]))

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not legal(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if legal(nx, ny):
                return [dx, dy]
        return [0, 0]

    if not targets:
        bestm, bestv = (0, 0), -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            v = -(abs(nx - ox) + abs(ny - oy))
            if v > bestv:
                bestv, bestm = v, (dx, dy)
        return [bestm[0], bestm[1]]

    # Deny opponent: pick resource where we can be relatively closer than opponent.
    selfp, opp = (sx, sy), (ox, oy)
    bestt, besttv = targets[0], -10**9
    for t in targets:
        dso = man(opp, t)
        dse = man(selfp, t)
        # prefer large positive (opponent farther than us); break ties toward nearer to avoid dithering
        tv = (dso - dse) * 10 - dse
        if tv > besttv:
            besttv, bestt = tv, t

    tx, ty = bestt
    bestm, bestv = (0, 0), -10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        dcur = man((nx, ny), (tx, ty))
        # slight repulsion from opponent to reduce chance of being forced backward
        dop = man((nx, ny), opp)
        v = -dcur * 3 - (1 if dop <= 1 else 0) * 5
        # if we can step onto/adjacent to target, strongly prefer it
        if nx == tx and ny == ty:
            v += 1000
        elif abs(nx - tx) <= 1 and abs(ny - ty) <= 1:
            v += 40
        # small tie-breaker: prefer moves that don't increase distance to target too much
        v -= 0.01 * man((sx, sy), (tx, ty)) if (nx, ny) == (sx, sy) else 0
        if v > bestv:
            bestv, bestm = v, (dx, dy)
    return [bestm[0], bestm[1]]