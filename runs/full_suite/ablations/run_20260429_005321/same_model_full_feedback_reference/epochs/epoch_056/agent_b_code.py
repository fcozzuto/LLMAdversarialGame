def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
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

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    # If no resources: move to increase distance from opponent (deny future pickup paths)
    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            val = d2(nx, ny, ox, oy)
            cand = (val, -nx, -ny, dx, dy)
            if best is None or cand > best:
                best = cand
        if best is None:
            return [0, 0]
        return [best[3], best[4]]

    # Otherwise: choose move that maximizes immediate capture advantage versus opponent over the best resource.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        my_next = 0
        # compute best resource-based advantage from this next position
        best_for_move = None
        for rx, ry in resources:
            myd = d2(nx, ny, rx, ry)
            opd = d2(ox, oy, rx, ry)
            # Prefer resources where we are closer than opponent; if we can't beat them, prefer resources where we are *least* behind.
            adv = opd - myd
            # Add slight tie-breaker: also prefer positions that keep opponent farther from the chosen resource.
            cand = (adv, opd, -myd, -rx, -ry, rx, ry)
            if best_for_move is None or cand > best_for_move:
                best_for_move = cand
        if best_for_move is None:
            continue
        # Combine into move score with extra preference for reducing our distance to the globally best resource option.
        adv, opd, nmyd, _, _, _, _ = best_for_move
        # nmyd is negative of myd; maximize it.
        cand_move = (adv, opd + nmyd * 0.01, nmyd, -dx, -dy, dx, dy)
        if best is None or cand_move > best:
            best = cand_move
            my_next = (nx, ny)

    if best is None:
        return [0, 0]
    return [best[4], best[5]]