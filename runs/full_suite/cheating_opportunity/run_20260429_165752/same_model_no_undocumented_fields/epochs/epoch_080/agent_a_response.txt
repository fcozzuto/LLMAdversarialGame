def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best_t = None
    best_v = -10**18
    if resources:
        for rx, ry in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            center = cheb(rx, ry, cx, cy)
            # Prefer winning races, then nearer/central targets; strongly punish being behind.
            v = (do - ds) * 20 + (12 - ds) * 2 - (center * 0.2)
            if ds == 0: v += 1e6
            if v > best_v:
                best_v = v
                best_t = (rx, ry)

    if best_t is None:
        # No visible resources; drift toward center while staying obstacle-safe.
        tx, ty = int(cx), int(cy)
    else:
        tx, ty = best_t

    # Choose move that improves our distance; if tie, maximize lead over opponent.
    best_m = (0, 0)
    best_mv = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        dsn = cheb(nx, ny, tx, ty)
        don = cheb(ox, oy, tx, ty)
        # Prefer smaller our distance; tie-break by larger opponent distance (lead).
        mv = (20 - dsn) * 100 + (don - dsn) * 10
        if tx == nx and ty == ny:
            mv += 1e7
        if mv > best_mv:
            best_mv = mv
            best_m = (nx - sx, ny - sy)

    return [int(best_m[0]), int(best_m[1])]