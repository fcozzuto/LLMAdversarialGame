def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

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

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    moves = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    # If no resources, drift toward center.
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy, nx, ny in moves:
            v = cheb(nx, ny, cx, cy)
            if best is None or v < best[0]:
                best = (v, dx, dy)
        return [best[1], best[2]]

    # Choose target resource: favor those we are closer to than opponent, then minimize our distance.
    best_t = None
    for rx, ry in resources:
        dme = cheb(sx, sy, rx, ry)
        dop = cheb(ox, oy, rx, ry)
        race = dop - dme  # higher means we are relatively closer
        # Deterministic tie-break: lower dop, then lower rx, then lower ry.
        key = (-(race), dme, dop, rx, ry)
        if best_t is None or key < best_t[0]:
            best_t = (key, rx, ry)
    _, tx, ty = best_t

    # Greedy move toward target with obstacle-safe neighbor evaluation.
    # Also keep away from opponent to reduce contest effectiveness.
    best = None
    for dx, dy, nx, ny in moves:
        dm = cheb(nx, ny, tx, ty)
        dopp = cheb(nx, ny, ox, oy)
        # Slightly prefer moves that keep opponent farther; penalize if we increase our distance.
        v = (dm * 10) - (dopp) + ((dm - cheb(sx, sy, tx, ty)) * 3)
        # Deterministic tie-break by direction order and coordinates.
        if best is None or (v, nx, ny, dx, dy) < best:
            best = (v, nx, ny, dx, dy)
    return [best[3], best[4]]