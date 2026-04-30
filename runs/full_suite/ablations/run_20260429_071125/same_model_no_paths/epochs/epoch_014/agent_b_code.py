def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def dist(a, b):
        return max(abs(a[0] - b[0]), abs(a[1] - b[1]))  # Chebyshev

    if not inside(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny):
                return [dx, dy]
        return [0, 0]

    if resources:
        best = None
        best_key = None
        for r in resources:
            md = dist((sx, sy), r)
            od = dist((ox, oy), r)
            # Prefer resources I'm closer to; if not, still prefer those where I can contest.
            key = (md, -(md - od), r[0], r[1])
            if best_key is None or key < best_key:
                best_key = key
                best = r
        tx, ty = best[0], best[1]
        target = (tx, ty)
    else:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best = None
        bestd = None
        for c in corners:
            if inside(c[0], c[1]):
                d = dist((ox, oy), c)
                if best is None or d > bestd:
                    best, bestd = c, d
        target = best if best is not None else (sx, sy)

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        nd_my = dist((nx, ny), target)
        nd_opp = dist((nx, ny), (ox, oy))
        # Greedy toward target; also avoid letting opponent get too close.
        score = nd_my * 10 - nd_opp
        # Small deterministic tie-break
        score2 = score * 1000 + (nx * 8 + ny)
        if best_score is None or score2 < best_score:
            best_score = score2
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]