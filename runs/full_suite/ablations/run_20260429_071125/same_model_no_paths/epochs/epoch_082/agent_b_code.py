def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    # Limit to most promising targets for speed/determinism
    resources.sort(key=lambda t: (cheb(sx, sy, t[0], t[1]), t[0], t[1]))
    resources = resources[:8]

    opp_d = {t: cheb(ox, oy, t[0], t[1]) for t in resources}

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_score = None
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not ok(nx, ny):
            continue
        # Score by best attainable advantage over any remaining target from next position
        best_adv = -10**9
        best_dist = 10**9
        best_tx = best_ty = 0
        for tx, ty in resources:
            myd = cheb(nx, ny, tx, ty)
            adv = (opp_d[(tx, ty)] - myd)
            if adv > best_adv or (adv == best_adv and (myd < best_dist or (myd == best_dist and (tx, ty) < (best_tx, best_ty)))):
                best_adv = adv
                best_dist = myd
                best_tx, best_ty = tx, ty
        score = (best_adv, -best_dist, -best_tx, -best_ty)  # maximize lexicographically
        if best_score is None or score > best_score:
            best_score = score
            best = (dxm, dym)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]