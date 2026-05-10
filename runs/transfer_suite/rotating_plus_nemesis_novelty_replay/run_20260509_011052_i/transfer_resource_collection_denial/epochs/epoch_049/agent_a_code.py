def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    res = []
    for p in (observation.get("resources") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                res.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not res:
        dx = 0 if (ox - sx) == 0 else (1 if (ox - sx) > 0 else -1)
        dy = 0 if (oy - sy) == 0 else (1 if (oy - sy) > 0 else -1)
        return [dx, dy]

    best_key = None
    best_t = None
    for x, y in res:
        sd = cheb(sx, sy, x, y)
        od = cheb(ox, oy, x, y)
        # Prefer resources where opponent is farther (od - sd positive), then shorter sd.
        key = (-(od - sd), sd, x, y)
        if best_key is None or key < best_key:
            best_key, best_t = key, (x, y)

    tx, ty = best_t
    if (sx, sy) == (tx, ty):
        return [0, 0]

    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = []
    for mx in (dx, 0, -dx):
        if mx == 0 and dx != 0:
            mx = 0
        for my in (dy, 0, -dy):
            if (mx, my) == (0, 0) or (mx != 0 and mx in (-1, 1)) or mx == 0:
                nx, ny = sx + mx, sy + my
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
                    d2t = cheb(nx, ny, tx, ty)
                    doa = cheb(nx, ny, ox, oy)
                    # Move that most reduces distance to target; tie-break to keep opponent away.
                    candidates.append((d2t, -doa, mx, my, nx, ny))
    if not candidates:
        return [0, 0]
    candidates.sort()
    return [int(candidates[0][2]), int(candidates[0][3])]