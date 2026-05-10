def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w, h = observation.get("grid_width", 1), observation.get("grid_height", 1)
    obs = set(observation.get("obstacles") or [])
    unclaimed = observation.get("unclaimed_cells") or []
    moves = [(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    if unclaimed:
        def dist(a, b, c, d):
            return abs(a - c) + abs(b - d)
        best_t = None
        best_val = None
        for ux, uy in unclaimed:
            dme = dist(sx, sy, ux, uy)
            dop = dist(ox, oy, ux, uy)
            val = (dme, -dop, ux, uy)
            if best_val is None or val < best_val:
                best_val = val
                best_t = (ux, uy)
        tx, ty = best_t
        def score(dx, dy, nx, ny):
            return dist(nx, ny, tx, ty) - 0.1 * dist(nx, ny, ox, oy)
        best = None
        for dx, dy, nx, ny in candidates:
            s = score(dx, dy, nx, ny)
            key = (s, dx, dy)
            if best is None or key < best[0]:
                best = (key, dx, dy)
        return [int(best[1]), int(best[2])]

    # Fallback: maximize distance from opponent, tie-break by move order
    best = None
    for i, (dx, dy, nx, ny) in enumerate([(m[0], m[1], sx + m[0], sy + m[1]) for m in moves] if True else []):
        if inb(nx, ny):
            key = (- (abs(nx - ox) + abs(ny - oy)), i)
            if best is None or key < best[0]:
                best = (key, dx, dy)
    if best is not None:
        return [int(best[1]), int(best[2])]
    return [0, 0]