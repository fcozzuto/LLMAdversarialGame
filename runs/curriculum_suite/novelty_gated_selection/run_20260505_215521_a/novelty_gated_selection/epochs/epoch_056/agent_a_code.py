def choose_move(observation):
    w = int(observation.get("grid_width", 0) or 0)
    h = int(observation.get("grid_height", 0) or 0)
    if w <= 0 or h <= 0:
        return [0, 0]

    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    res = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))
    if not res:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def d(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    # Identify the resource the opponent is currently closest to (contested objective).
    best_cont = None
    best_od = 10**18
    for rr in res:
        od = d((ox, oy), rr)
        if od < best_od or (od == best_od and (rr[0], rr[1]) < (best_cont[0], best_cont[1])):
            best_od = od
            best_cont = rr
    target = best_cont

    best = None  # (score, -ourDist, dx, dy)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obst:
            continue

        ourd_t = d((nx, ny), target)
        oppd_t = d((ox, oy), target)  # opponent doesn't move this turn in our heuristic

        # Denial/intercept: try to become closer to the contested resource than opponent is right now.
        score = (oppd_t - ourd_t) * 25

        # Also ensure we don't abandon all resources.
        our_best = 10**18
        opp_best = 10**18
        for rr in res:
            our_best = min(our_best, d((nx, ny), rr))
            opp_best = min(opp_best, d((ox, oy), rr))
        score += (opp_best - our_best) * 10

        # Mild obstacle/edge preference: avoid stepping into corners far from target if already behind.
        if ourd_t > best_od:
            edge = (nx == 0 or nx == w - 1 or ny == 0 or ny == h - 1)
            score -= 3 if edge else 0

        cand = (score, -ourd_t, dx, dy)
        if best is None or cand > best:
            best = cand

    if best is None:
        return [0, 0]
    return [best[2], best[3]]