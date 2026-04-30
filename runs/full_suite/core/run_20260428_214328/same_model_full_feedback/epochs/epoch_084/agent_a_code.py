def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def score_target(tx, ty):
        sd = cheb(sx, sy, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # Prefer resources where we are strictly closer; otherwise contest with lower priority.
        return (od - sd) * 100 - sd + (1 if (tx == (w - 1) and ty == (h - 1)) else 0)

    if not resources:
        # Deterministic fallback: drift toward center.
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        bestd = 10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            if d < bestd:
                bestd = d
                best = (dx, dy)
        return list(best if best is not None else (0, 0))

    best_tx, best_ty = resources[0]
    best_val = -10**18
    for tx, ty in resources:
        val = score_target(tx, ty)
        if val > best_val or (val == best_val and (tx, ty) < (best_tx, best_ty)):
            best_val = val
            best_tx, best_ty = tx, ty

    # Choose next step: minimize our distance to target; tie-break by maximizing opponent distance to same target.
    best_move = (0, 0)
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd = cheb(nx, ny, best_tx, best_ty)
        opd = cheb(ox, oy, best_tx, best_ty)
        # Slightly prefer moves that also increase our distance from opponent (more space to maneuver).
        back = cheb(nx, ny, ox, oy)
        key = (myd, -back, -opd)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    # If somehow all moves invalid, stay.
    return [int(best_move[0]), int(best_move[1])]