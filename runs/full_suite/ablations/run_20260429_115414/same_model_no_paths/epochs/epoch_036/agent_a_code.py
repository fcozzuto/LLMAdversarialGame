def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if not resources:
        best = (0, 0)
        bestv = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): 
                continue
            v = -cheb(nx, ny, ox, oy)
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            v += -0.02 * (abs(nx - cx) + abs(ny - cy))
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # Pick a target resource where we are closer than opponent (or at least improve over them).
    # Then choose a step that minimizes our distance to that target while avoiding stepping into blocks.
    best_target = resources[0]
    best_adv = -10**18
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        adv = (opd - myd) * 10 - myd  # prioritize winning contests, then proximity
        # slight bias toward resources not adjacent to opponent
        adv += -2 if cheb(ox, oy, rx, ry) <= 1 else 0
        if adv > best_adv:
            best_adv = adv
            best_target = (rx, ry)

    tx, ty = best_target
    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        myd2 = cheb(nx, ny, tx, ty)
        opd2 = cheb(ox, oy, tx, ty)
        # Improve our step quality; also discourage moves that allow opponent to be closer at next capture race.
        v = (opd2 - myd2) * 10 - myd2
        # If we can't win, still move to deny: increase our value by reducing distance to opponent while heading to target.
        v += 0.3 * (cheb(nx, ny, ox, oy) * -1)
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        v += -0.02 * (abs(nx - cx) + abs(ny - cy))
        if v > best_val:
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]