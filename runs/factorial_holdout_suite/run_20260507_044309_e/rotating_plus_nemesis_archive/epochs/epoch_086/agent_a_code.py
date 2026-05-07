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
        da = abs(a - c)
        db = abs(b - d)
        return da if da > db else db

    def resource_score(tx, ty):
        myd = cheb(sx, sy, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        return (opd - myd, -myd, -(cheb(ox, oy, tx, ty)))

    resources.sort()
    target = max(resources, key=lambda t: (resource_score(t[0], t[1])))

    tx, ty = target
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    deltas.sort()
    best_move = [0, 0]
    best_val = None

    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        myd = cheb(nx, ny, tx, ty)
        opd = cheb(ox, oy, tx, ty)
        step_to = abs(nx - tx) + abs(ny - ty)
        myd_now = cheb(sx, sy, tx, ty)
        progress = myd_now - myd
        val = (progress, (opd - myd), -myd, -step_to, -abs(nx - ox) - abs(ny - oy), -abs(nx - sx) - abs(ny - sy))
        if best_val is None or val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move