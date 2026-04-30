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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # deterministic fallback: drift toward central while staying valid
        cx, cy = 3, 3
        tx, ty = (3, 3) if cheb(sx, sy, 3, 3) <= cheb(sx, sy, 4, 4) else (4, 4)
        best = (10**9, 10**9, 0, 0)
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            # avoid moving away from center too much
            dc = cheb(nx, ny, cx, cy)
            key = (d, dc, dx, dy)
            if key < best:
                best = key
        return [best[2], best[3]]

    # Choose target resource that maximizes potential advantage (opp closer => worse)
    best_target = None
    best_tkey = None
    for x, y in resources:
        ds = cheb(sx, sy, x, y)
        do = cheb(ox, oy, x, y)
        # maximize (do - ds); tie-break toward smaller ds, then deterministic position
        adv = do - ds
        key = (-adv, ds, x, y)
        if best_tkey is None or key < best_tkey:
            best_tkey = key
            best_target = (x, y)

    tx, ty = best_target

    # One-step lookahead: pick move that maximizes (opp_dist - self_dist) to the chosen target,
    # and secondarily minimizes own distance to it.
    best_m = None
    best_mkey = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds2 = cheb(nx, ny, tx, ty)
        do2 = cheb(ox, oy, tx, ty)
        score_adv = do2 - ds2  # higher is better
        # tie-break: smallest ds2, then move ordering deterministic
        key = (-score_adv, ds2, dx, dy)
        if best_mkey is None or key < best_mkey:
            best_mkey = key
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]