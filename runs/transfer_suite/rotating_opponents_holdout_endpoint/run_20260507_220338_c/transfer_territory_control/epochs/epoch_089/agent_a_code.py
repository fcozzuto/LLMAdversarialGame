def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inside(x, y):
                blocked.add((x, y))

    selfT = set()
    for t in observation.get("self_territory") or []:
        if t is not None and len(t) >= 2:
            selfT.add((int(t[0]), int(t[1])))

    oppT = set()
    for t in observation.get("opponent_territory") or []:
        if t is not None and len(t) >= 2:
            oppT.add((int(t[0]), int(t[1])))

    unclaimed = set()
    for t in observation.get("unclaimed_cells") or []:
        if t is not None and len(t) >= 2:
            unclaimed.add((int(t[0]), int(t[1])))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    targets = list(unclaimed) if unclaimed else list(oppT) if oppT else []
    # deterministic nearest target distances
    if targets:
        nt = None
        nd = 10**9
        for t in targets:
            d = abs(t[0] - sx) + abs(t[1] - sy)
            if d < nd:
                nd, nt = d, t
    else:
        nt = (ox, oy)

    best = (0, 0)
    bestv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        if (nx, ny) in blocked:
            continue
        v = 0
        if (nx, ny) in selfT:
            v += 1.5
        if (nx, ny) in unclaimed:
            v += 3.5
        if (nx, ny) in oppT:
            v += 4.0  # likely flip on entry (flipping enabled)
        # bias toward expanding into frontier
        dist_to_nt = abs(nx - nt[0]) + abs(ny - nt[1])
        v += 2.0 / (1 + dist_to_nt)
        # avoid running straight into opponent when possible
        dist_to_opp = abs(nx - ox) + abs(ny - oy)
        v += 0.6 * (dist_to_opp)
        # slight preference to corner/edge (helps territory sweepers)
        v += 0.05 * (min(nx, w - 1 - nx, ny, h - 1 - ny))
        if v > bestv:
            bestv = v
            best = (dx, dy)

    return [int(best[0]), int(best[1])]