def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources") or []):
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        best = None
        for tx, ty in resources:
            md = cheb(sx, sy, tx, ty)
            od = cheb(ox, oy, tx, ty)
            adv = od - md
            occupy_bias = 1 if (tx, ty) == (sx, sy) else 0
            center = cheb(tx, ty, (w - 1) // 2, (h - 1) // 2)
            key = (adv, occupy_bias, -md, -center, tx, ty)
            if best is None or key > best[0]:
                best = (key, (tx, ty))
        tx, ty = best[1]

    best_move = (0, 0)
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_self = cheb(nx, ny, tx, ty)
        d_opp = cheb(ox, oy, tx, ty)
        adv = d_opp - d_self
        step_center = cheb(nx, ny, (w - 1) // 2, (h - 1) // 2)
        k = (adv, -d_self, -step_center, dx, dy)
        if best_key is None or k > best_key:
            best_key = k
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]