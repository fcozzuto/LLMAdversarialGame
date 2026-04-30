def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d2(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        return dx * dx + dy * dy

    def nearest_dist2(ax, ay):
        if not resources:
            tx, ty = (w - 1) // 2, (h - 1) // 2
            return d2(ax, ay, tx, ty), (tx, ty)
        best = None
        best_r = None
        for rx, ry in resources:
            v = d2(ax, ay, rx, ry)
            if best is None or v < best:
                best, best_r = v, (rx, ry)
        return best, best_r

    _, fallback = nearest_dist2(sx, sy)

    if resources:
        # Choose the resource where we have the most distance advantage over opponent.
        best_adv = None
        target = fallback
        for rx, ry in resources:
            my = d2(sx, sy, rx, ry)
            opd = d2(ox, oy, rx, ry)
            # Prefer strict advantage; tie-break deterministically by coordinates.
            adv = (opd - my, -my)  # higher adv is better, then closer
            if best_adv is None or adv > best_adv or (adv == best_adv and (rx, ry) < target):
                best_adv = adv
                target = (rx, ry)
    else:
        target = fallback

    tx, ty = target
    # Greedy move: reduce distance to chosen target; if tie, prefer reducing opponent's advantage gap.
    best_move = (0, 0)
    best_score = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        myd = d2(nx, ny, tx, ty)
        if resources:
            # Estimate opponent's distance to same target to bias contest positions.
            opd = d2(ox, oy, tx, ty)
            score = (-(myd), -(opd - myd))  # prioritize small myd; then contest pressure
        else:
            score = (-myd, 0)
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]