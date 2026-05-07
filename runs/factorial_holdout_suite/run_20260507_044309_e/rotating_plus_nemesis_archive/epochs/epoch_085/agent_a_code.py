def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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
    if not resources:
        return [0, 0]

    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    def score_target(t):
        tx, ty = t
        myd = cheb(sx, sy, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        # Prefer resources where we are closer; then minimize our distance; then prefer farther from opponent (safer)
        return (opd - myd, -myd, -(cheb(ox, oy, tx, ty)))

    target = resources[0]
    best = score_target(target)
    for r in resources[1:]:
        sr = score_target(r)
        if sr > best:
            best = sr
            target = r

    tx, ty = target
    actions = []
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                actions.append((dx, dy))

    if not actions:
        return [0, 0]

    # Move greedily toward target with a small deterrent from being too close to opponent
    best_act = None
    best_val = 10**18
    for dx, dy in actions:
        nx, ny = sx + dx, sy + dy
        myd_next = cheb(nx, ny, tx, ty)
        opd_next = cheb(nx, ny, ox, oy)
        val = myd_next * 10 - opd_next  # smaller is better
        if val < best_val:
            best_val = val
            best_act = [dx, dy]
        elif val == best_val:
            # Deterministic tie-break: prefer staying if equally good, else lexicographic on (dx,dy)
            if best_act is None or (dx == 0 and dy == 0 and not (best_act[0] == 0 and best_act[1] == 0)) or (dx, dy) < (best_act[0], best_act[1]):
                best_act = [dx, dy]

    return best_act if best_act is not None else [0, 0]