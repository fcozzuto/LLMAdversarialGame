def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        dy = ay - by
        if dx < 0:
            dx = -dx
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        open_n = 0
        for adx, ady in moves:
            tx, ty = nx + adx, ny + ady
            if inb(tx, ty) and (tx, ty) not in obs:
                open_n += 1
        if resources:
            best = None
            for rx, ry in resources:
                sd = cheb(nx, ny, rx, ry)
                od = cheb(nx, ny, ox, oy) - cheb(rx, ry, ox, oy)  # approximate denial pressure via turn-advantage
                # Main: want to be closer than opponent to that resource
                den = cheb(nx, ny, rx, ry) - cheb(rx, ry, ox, oy)
                # Prefer immediate reach and deny
                v = (-den, -sd, open_n, rx, ry)
                if best is None or v > best:
                    best = v
            # also lightly prefer moving toward the "better" resources for global consistency
            candidates.append((best[0], best[1], best[2], dx, dy))
        else:
            tx, ty = w // 2, h // 2
            v = (-cheb(nx, ny, tx, ty), open_n, -cheb(nx, ny, ox, oy))
            candidates.append((v[0], v[1], v[2], dx, dy))

    if not candidates:
        return [0, 0]

    # Deterministic tie-break using move order already embedded by comparisons
    candidates.sort(reverse=True)
    return [int(candidates[0][3]), int(candidates[0][4])]