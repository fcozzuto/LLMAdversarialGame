def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    opp = observation.get("opponent_position") or [w - 1, h - 1]
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    candidates = observation.get("unclaimed_cells") or []
    best = None
    bestv = -10**18
    for c in candidates[:80]:
        if not (isinstance(c, (list, tuple)) and len(c) >= 2):
            continue
        x, y = int(c[0]), int(c[1])
        if not inside(x, y) or (x, y) in obs:
            continue
        d1 = (x - sx) * (x - sx) + (y - sy) * (y - sy)
        d2 = (x - ox) * (x - ox) + (y - oy) * (y - oy)
        v = d2 - d1  # prefer far from opponent, near self
        if v > bestv:
            bestv = v
            best = (x, y)

    if best is None:
        best = ((w - 1) // 2, (h - 1) // 2)

    tx, ty = best
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    bestm = (0, 0)
    bestd = 10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny) or (nx, ny) in obs:
            continue
        d = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        if d < bestd or (d == bestd and (dx, dy) < bestm):
            bestd = d
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]