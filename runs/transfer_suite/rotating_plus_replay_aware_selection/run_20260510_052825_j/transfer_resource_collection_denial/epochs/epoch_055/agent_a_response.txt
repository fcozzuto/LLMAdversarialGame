def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles", []) or [])}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def best_target():
        best = None
        for p in resources:
            rx, ry = p[0], p[1]
            if not inb(rx, ry) or (rx, ry) in obstacles:
                continue
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer resources where we are at least as fast; then maximize (od-sd);
            # then minimize our distance; then smallest coordinates for determinism.
            adv = od - sd
            key = (0 if adv >= 0 else 1, -adv, sd, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        return None if best is None else best[1]

    target = best_target()
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if target is None:
        # No reachable resources: move toward board center deterministically
        cx, cy = (w - 1) // 2, (h - 1) // 2
        bestm = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            key = (cheb(nx, ny, cx, cy), nx, ny)
            if bestm is None or key < bestm[0]:
                bestm = (key, (dx, dy))
        return list(bestm[1]) if bestm is not None else [0, 0]

    tx, ty = target
    # If we can step onto target, do it.
    dx0 = tx - sx
    dy0 = ty - sy
    if abs(dx0) <= 1 and abs(dy0) <= 1:
        step = [0, 0]
        if dx0 != 0:
            step[0] = 1 if dx0 > 0 else -1
        if dy0 != 0:
            step[1] = 1 if dy0 > 0 else -1
        nx, ny = sx + step[0], sy + step[1]
        if inb(nx, ny) and (nx, ny) not in obstacles:
            return step

    # Otherwise, greedily reduce our distance to target, while ensuring we don't hand over a closer resource.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nsd = cheb(nx, ny, tx, ty)
        nod = cheb(ox, oy, tx, ty)
        # primary: minimize our remaining distance
        # secondary: prefer states where we are not behind opponent on this target
        key = (0 if nsd <= nod else 1, nsd, nod - nsd, nx, ny)
        if best is None or key < best[0]:
            best = (key, (dx, dy))
    return list(best[1]) if best is not None else [0, 0]