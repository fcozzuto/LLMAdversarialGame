def choose_move(observation):
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [W - 1, H - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obstacles:
                resources.append((x, y))

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inside(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obstacles

    # Choose best target deterministically by "who arrives first" advantage.
    target = None
    if resources:
        best = None
        for rx, ry in resources:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Primary: maximize (od - sd). Secondary: smaller sd. Tertiary: farther sd (tie-break).
            val = (od - sd, -sd, sd)
            if best is None or val > best[0]:
                best = (val, rx, ry)
        target = (best[1], best[2])

    # If no resources, go to center; otherwise move greedily toward target.
    if target is None:
        tx, ty = W // 2, H // 2
    else:
        tx, ty = target

    best_move = (0, 0)
    best_score = None
    pref = 0  # deterministic preference: try moves in deltas order; tie-break by lexicographic
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        # Score: closer to target, also slightly discourage positions that let opponent get closer to same target.
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        myd_now = cheb(sx, sy, tx, ty)
        # Opponent can't move here, but a heuristic: if we reduce our distance while opponent is already nearer, prioritize.
        score = (-myd, (opd - myd), -abs(nx - W//2) - abs(ny - H//2), -pref)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
        pref += 1

    return [int(best_move[0]), int(best_move[1])]