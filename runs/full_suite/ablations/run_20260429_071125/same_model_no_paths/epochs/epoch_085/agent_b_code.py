def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if valid(x, y):
                resources.append((x, y))
    if not resources:
        return [0, 0]

    best_r = None
    best_score = None
    for x, y in resources:
        ds = cheb(sx, sy, x, y)
        do = cheb(ox, oy, x, y)
        score = ds * 2 - do  # prefer close to us, far from opponent
        if best_score is None or score < best_score or (score == best_score and (x, y) < best_r):
            best_score = score
            best_r = (x, y)

    tx, ty = best_r
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best_m = (0, 0)
    best_h = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dn = cheb(nx, ny, tx, ty)
        # small tie-break: reduce distance to opponent (more contention)
        hval = dn * 2 - cheb(ox, oy, tx, ty) + 0.05 * cheb(nx, ny, ox, oy)
        if best_h is None or hval < best_h or (hval == best_h and (dx, dy) < best_m):
            best_h = hval
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]