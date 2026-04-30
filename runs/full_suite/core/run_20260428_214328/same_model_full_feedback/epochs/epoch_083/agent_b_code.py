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

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    if resources:
        best_tx, best_ty = None, None
        best_val = -10**9
        for tx, ty in resources:
            md = cheb(sx, sy, tx, ty)
            od = cheb(ox, oy, tx, ty)
            adv = (2 if md <= od else 0) + (1 if md < od else 0)  # prefer contested/closer
            block_pref = 0.0
            if md == od:
                # if tied, prefer resources more away from opponent to reduce collision likelihood
                block_pref = (1.0 / (1 + od))
            val = adv - 0.03 * md + block_pref
            if val > best_val:
                best_val = val
                best_tx, best_ty = tx, ty
    else:
        best_tx, best_ty = cx, cy

    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        myd = cheb(nx, ny, best_tx, best_ty)
        opd = cheb(ox, oy, best_tx, best_ty)
        dist_to_op = cheb(nx, ny, ox, oy)
        # primary: get closer to target; secondary: avoid moving into opponent's vicinity when not improving
        score = (-2.0 * myd) + (0.35 * dist_to_op) + (0.2 if myd <= opd else 0.0)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]