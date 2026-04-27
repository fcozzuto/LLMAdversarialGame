def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def md(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def cell_ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    tx, ty = sx, sy
    if resources:
        best = None
        bestv = None
        for r in resources:
            myd = md((sx, sy), r)
            opd = md((ox, oy), r)
            race = opd - myd
            cen = -abs((w - 1) / 2 - r[0]) - abs((h - 1) / 2 - r[1])
            val = race * 1000 + cen * 3 - (myd)
            tieb = (-(race), -cen, myd, r[0], r[1])
            if best is None or val > bestv or (val == bestv and tieb < best):
                bestv = val
                best = tieb
                tx, ty = r
    else:
        # No resources: drift to center line between us and opponent
        mx = (sx + ox) // 2
        my = (sy + oy) // 2
        tx = max(0, min(w - 1, mx))
        ty = max(0, min(h - 1, my))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = (0, 0)
    bestv = -10**18
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not cell_ok(nx, ny):
            continue
        myd = md((nx, ny), (tx, ty))
        opd = md((ox, oy), (tx, ty))
        race = opd - myd
        # Prefer moves that keep us closer to target and improve our race vs opponent.
        val = race * 1000 - myd + (nx - sx) * 0 + (ny - sy) * 0
        # Deterministic tie-break: lexicographic on move delta.
        if val > bestv or (val == bestv and (dx, dy) < bestm):
            bestv = val
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]