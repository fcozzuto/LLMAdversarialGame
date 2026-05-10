def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    resources = observation.get("resources", []) or []
    targets = []
    for r in resources:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if valid(rx, ry):
                targets.append((rx, ry))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if targets:
        best_t = None
        best_val = None
        for rx, ry in targets:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Prefer resources where we are closer; slightly prefer shorter absolute distance.
            val = (myd - opd) * 10 + myd
            if best_val is None or val < best_val or (val == best_val and (rx, ry) < best_t):
                best_val = val
                best_t = (rx, ry)
        tx, ty = best_t
        # Greedy one-step move minimizing distance to target, with tie-breakers favoring "forward" progress.
        best_move = [0, 0]
        best_d = None
        best_sc = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            sc = (d, -(abs(nx - tx) + abs(ny - ty)), nx, ny)
            if best_d is None or d < best_d or (d == best_d and sc < best_sc):
                best_d = d
                best_sc = sc
                best_move = [dx, dy]
        return best_move

    # No visible resources: head to center deterministically.
    cx, cy = w // 2, h // 2
    best_move = [0, 0]
    best_d = None
    best_sc = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = cheb(nx, ny, cx, cy)
        sc = (d, nx, ny)
        if best_d is None or d < best_d or (d == best_d and sc < best_sc):
            best_d = d
            best_sc = sc
            best_move = [dx, dy]
    return best_move