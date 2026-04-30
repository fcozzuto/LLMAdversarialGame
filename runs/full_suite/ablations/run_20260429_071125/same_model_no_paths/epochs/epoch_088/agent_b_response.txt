def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
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
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))

    def step_sign(a):
        return 1 if a > 0 else (-1 if a < 0 else 0)

    if resources:
        best = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds  # bigger => better for us
            cand = ( -adv, ds, rx, ry)  # minimize
            if best is None or cand < best:
                best = cand
        _, _, tx, ty = best
    else:
        cx, cy = w // 2, h // 2
        # if opponent is closer to center, bias slightly away from them
        if cheb(ox, oy, cx, cy) < cheb(sx, sy, cx, cy):
            tx = 0 if ox > sx else w - 1
            ty = 0 if oy > sy else h - 1
        else:
            tx, ty = cx, cy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    # candidate deltas deterministic order, prefer straight/forward toward target
    cand_deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    scored = []
    for dx, dy in cand_deltas:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist = cheb(nx, ny, tx, ty)
        opp_close = cheb(nx, ny, ox, oy)
        penalty = 2 if opp_close <= 1 else 0
        scored.append((dist + penalty, -cheb(nx, ny, ox, oy), dx, dy))
    if scored:
        scored.sort()
        return [int(scored[0][2]), int(scored[0][3])]

    # fallback: try simple sign step if valid
    dx = step_sign(tx - sx)
    dy = step_sign(ty - sy)
    nx, ny = sx + dx, sy + dy
    if valid(nx, ny):
        return [int(dx), int(dy)]
    return [0, 0]