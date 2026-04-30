def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

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
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                resources.append((rx, ry))

    # If no resources, drift to center while staying valid.
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    target = None
    if resources:
        best = None
        bestv = None
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer resources where we can "beat" the opponent in distance, then closer to us.
            # Tie-break deterministically by coordinates.
            v = (do - ds) * 10000 - ds * 10 - (abs(rx - cx) + abs(ry - cy))
            key = (v, -rx, -ry)
            if best is None or key > best:
                best = key
                bestv = (rx, ry)
        target = bestv

    tx, ty = target if target is not None else (cx, cy)

    # Choose the move that most improves our distance advantage to the target.
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ns = cheb(nx, ny, tx, ty)
        os = cheb(ox, oy, tx, ty)
        # Also add a small term to avoid getting stuck near obstacles: prefer smaller distance to center as secondary.
        score = (os - ns) * 10000 - ns * 10 - cheb(nx, ny, cx, cy)
        key = (score, -dx, -dy, nx, ny)  # deterministic tie-break
        if best_score is None or key > best_score:
            best_score = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]