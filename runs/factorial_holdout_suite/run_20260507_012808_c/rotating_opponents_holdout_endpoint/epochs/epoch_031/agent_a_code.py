def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    w = int(w) if isinstance(w, (int, float, str)) else 8
    h = int(h) if isinstance(h, (int, float, str)) else 8

    sp = observation.get("self_position", (0, 0))
    op = observation.get("opponent_position", (0, 0))
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    # Target resource: maximize our advantage (opp distance - our distance),
    # while still preferring closer resources; deterministic tiebreak by coords.
    best = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        adv = od - sd
        # If opponent is closer on one axis, add mild penalty to reduce contest likelihood.
        axis_pen = 0
        if rx == ox and sy != ry:
            axis_pen += 1 if abs(ry - sy) >= abs(ry - oy) else 0
        if ry == oy and sx != rx:
            axis_pen += 1 if abs(rx - sx) >= abs(rx - ox) else 0
        key = (adv, -sd, -axis_pen, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best

    # Greedy move toward target with obstacle-aware local sidesteps.
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = []
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    for ddx, ddy in deltas:
        nx, ny = sx + ddx, sy + ddy
        if not ok(nx, ny):
            continue
        # Prefer chebyshev distance reduction to target, then avoid stepping adjacent to opponent.
        nd = cheb(nx, ny, tx, ty)
        cd = cheb(sx, sy, tx, ty)
        dist_gain = cd - nd
        opp_adj = cheb(nx, ny, ox, oy)
        opp_pen = 2 if opp_adj <= 1 else 0
        # Deterministic tiebreak: lexicographic by (nx, ny) through dd ordering.
        candidates.append((dist_gain - opp_pen, -nd, nx, ny, ddx, ddy))

    if not candidates:
        return [0, 0]
    candidates.sort(reverse=True)
    return [int(candidates[0][4]), int(candidates[0][5])]