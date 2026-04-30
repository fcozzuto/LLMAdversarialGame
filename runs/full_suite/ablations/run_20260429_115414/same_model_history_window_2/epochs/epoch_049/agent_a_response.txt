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

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                resources.append((rx, ry))

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        best_move = (0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            dcen = max(abs(nx - cx), abs(ny - cy))
            dop = max(abs(nx - ox), abs(ny - oy))
            score = (dcen, -dop, dx, dy)
            if best is None or score < best:
                best = score
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best = None
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Choose a resource to "aim" at: minimize our distance, then maximize lead over opponent.
        best_for_move = None
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            lead = do - ds  # positive means we are closer than opponent
            # Also slightly prefer moving onto a resource immediately.
            hit = 1 if (nx == rx and ny == ry) else 0
            cand = (-hit, ds, -lead, rx, ry)
            if best_for_move is None or cand < best_for_move:
                best_for_move = cand

        # Secondary evaluation across all resources: prefer moves that improve our nearest distance,
        # while breaking ties by keeping distance from the opponent.
        nearest_after = best_for_move[1] if best_for_move is not None else cheb(nx, ny, resources[0][0], resources[0][1])
        dop_after = cheb(nx, ny, ox, oy)
        score = (nearest_after, -dop_after, dx, dy, best_for_move[0] if best_for_move else 0)

        if best is None or score < best:
            best = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]