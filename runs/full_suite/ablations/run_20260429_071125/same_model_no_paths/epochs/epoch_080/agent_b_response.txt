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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Primary: maximize opponent disadvantage. Secondary: minimize my distance.
        key = (opd - myd, -myd, -(rx), -(ry))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)
    tx, ty = best

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
                myd = cheb(nx, ny, tx, ty)
                myd0 = cheb(sx, sy, tx, ty)
                opd = cheb(ox, oy, tx, ty)
                # Encourage reducing distance, and improving advantage versus opponent.
                adv = (opd - myd) - (opd - myd0)
                # Slightly discourage stepping away from the target.
                toward = myd0 - myd
                # Deterministic tie-breaker prefers smaller dx/dy magnitude.
                tie = -(abs(dx) + abs(dy))
                score = adv * 1000 + toward * 10 - myd
                candidates.append((score, tie, dx, dy))
    candidates.sort(reverse=True)
    return [int(candidates[0][2]), int(candidates[0][3])]