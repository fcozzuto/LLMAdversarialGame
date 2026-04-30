def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def best_step_towards(tx, ty):
        best = (10**9, 10**9, 0, 0)
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    pass
                nx, ny = sx + dx, sy + dy
                if not (0 <= nx < w and 0 <= ny < h):
                    continue
                if (nx, ny) in obstacles:
                    continue
                d1 = cheb(nx, ny, tx, ty)
                d2 = cheb(nx, ny, ox, oy)
                # Prefer decreasing our distance to target; if tied, increase distance to opponent
                cand = (d1, -d2, nx, ny)
                if cand < best:
                    best = cand
        return (best[2] - sx, best[3] - sy)

    # Target selection: maximize our advantage (opponent distance minus our distance),
    # while preferring closer targets when our advantage is similar.
    best_target = None
    best_key = (-10**9, 10**9, 10**9)
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        adv = opd - myd
        key = (adv, myd, -rx - ry)  # deterministic tie-breaker
        if key > best_key:
            best_key = key
            best_target = (rx, ry)

    tx, ty = best_target
    dx, dy = best_step_towards(tx, ty)

    # If already blocked (shouldn't happen), fall back to staying put.
    if not (-1 <= dx <= 1 and -1 <= dy <= 1):
        return [0, 0]
    return [int(dx), int(dy)]