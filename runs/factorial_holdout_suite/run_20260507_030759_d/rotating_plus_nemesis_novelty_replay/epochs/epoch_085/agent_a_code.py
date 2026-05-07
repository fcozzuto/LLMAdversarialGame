def choose_move(observation):
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # pick resource where we have temporal advantage; otherwise closest race
    best = None
    best_key = None
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        adv = opd - myd  # positive means we arrive first
        # tie-break to reduce pathing ambiguity: slight preference for lower x+y and being more central-ish
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dist_center = abs(rx - cx) + abs(ry - cy)
        key = (adv, -myd, dist_center, (rx + ry))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    dx = 0
    dy = 0
    if tx > sx: dx = 1
    elif tx < sx: dx = -1
    if ty > sy: dy = 1
    elif ty < sy: dy = -1

    # If stepping diagonally is "unhelpful" (still deterministic), prefer axis step when it doesn't worsen cheb distance
    if dx != 0 and dy != 0:
        d_diag = cheb(sx + dx, sy + dy, tx, ty)
        d_x = cheb(sx + dx, sy, tx, ty)
        d_y = cheb(sx, sy + dy, tx, ty)
        if d_x <= d_diag and d_x <= d_y:
            dy = 0
        elif d_y <= d_diag and d_y <= d_x:
            dx = 0

    nx, ny = sx + dx, sy + dy
    if (nx, ny) in obstacles:
        # simple fallback: try axis that still reduces distance the most
        cand = [(dx, 0), (0, dy), (0, 0)]
        bestd = None
        bestm = (0, 0)
        for mx, my in cand:
            ax, ay = sx + mx, sy + my
            if (ax, ay) in obstacles:
                continue
            dd = cheb(ax, ay, tx, ty)
            if bestd is None or dd < bestd or (dd == bestd and (mx != 0)):
                bestd = dd
                bestm = (mx, my)
        return [int(bestm[0]), int(bestm[1])]

    return [int(dx), int(dy)]