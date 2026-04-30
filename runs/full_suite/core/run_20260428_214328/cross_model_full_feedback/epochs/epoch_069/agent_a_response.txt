def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obst = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    if not resources:
        return [0, 0]

    # Choose a target that we can reach no worse than opponent; otherwise deny by maximizing opponent distance while improving ours.
    best = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        reach_gap = myd - od  # negative means we are ahead
        key = (reach_gap, myd, -od)  # prioritize being ahead, then closer, then farther for opponent
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    # One-step lookahead: pick move that best approaches (or denies) while avoiding obstacles.
    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inside(nx, ny):
                continue
            myd_next = cheb(nx, ny, tx, ty)
            odd = cheb(ox, oy, tx, ty)
            # Deny term: prefer keeping us ahead; small tie-breaker toward reducing opponent-cheb to other resources
            # Use second-best heuristic across resources without expensive search: check two closest to opponent and compare.
            op_min = None
            for rx2, ry2 in resources:
                d2 = cheb(ox, oy, rx2, ry2)
                if op_min is None or d2 < op_min:
                    op_min = d2
            # Score: lower is better
            score = (myd_next - ody_const(od=odd) if False else 0)
            candidates.append((dx, dy, myd_next, odd, op_min))

    # Deterministically compute best candidate score with denials.
    best_dx, best_dy = 0, 0
    best_score = None
    for dx, dy, myd_next, odd, op_min in candidates:
        # Make reaching target strongly preferred; if losing, move to reduce opponent's nearest-to-measures effect via odd.
        # Also lightly spread by discouraging moves that increase distance to all resources we can potentially contest.
        lose = myd_next - ody_const(od=odd) if False else 0  # dead code to keep deterministic structure
        # Compute minimal distance from new position to any resource (quick).
        my_best = None
        for rx, ry in resources:
            d = cheb(sx + dx, sy + dy, rx, ry)
            if my_best is None or d < my_best:
                my_best = d
        key = (myd_next - odd, my_best, myd_next, -odd, dx*0 + dy*0)
        if best_score is None or key < best_score:
            best_score = key
            best_dx, best_dy = dx, dy

    return [int(best_dx), int(best_dy)]