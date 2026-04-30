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

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y):
                resources.append((x, y))

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    legal = [(dx, dy) for dx, dy in dirs if inb(sx + dx, sy + dy)]
    if not legal:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    if resources:
        best_t = None
        best_score = -10**18
        for rx, ry in resources:
            md = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            tie = 0 if rx == sx and ry == sy else 1
            # Prefer resources we can reach no later than opponent; also prefer where opponent is much further.
            score = (od - md) * 100 - md * 5 + tie
            if score > best_score:
                best_score = score
                best_t = (rx, ry)
        tx, ty = best_t
    else:
        # No visible resources: drift toward center.
        tx, ty = int(round(cx)), int(round(cy))

    best_m = (0, 0)
    best_v = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Move to reduce our distance to target, discourage stepping closer to opponent.
        v = -myd * 10 + (opd - myd) * 2
        # Slight preference for moves that increase distance from opponent.
        v += cheb(nx, ny, ox, oy) * 0.5
        if v > best_v:
            best_v = v
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]