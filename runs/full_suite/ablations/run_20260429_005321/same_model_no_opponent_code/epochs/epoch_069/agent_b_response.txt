def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d2(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        return dx * dx + dy * dy

    def adj_block(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if (nx, ny) in obstacles:
                    return 1
        return 0

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                moves.append((dx, dy, nx, ny))
    if not moves:
        return [0, 0]

    if resources:
        best_t = resources[0]
        best_key = None
        for t in resources:
            ds = d2((sx, sy), t)
            do = d2((ox, oy), t)
            key = (ds - do, -do, ds, t[0], t[1])
            if best_key is None or key < best_key:
                best_key = key
                best_t = t
        tx, ty = best_t
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    cur_d = d2((sx, sy), (tx, ty))
    best = None
    best_s = None
    for dx, dy, nx, ny in moves:
        nd = d2((nx, ny), (tx, ty))
        od = d2((nx, ny), (ox, oy))
        # Prefer getting closer to target, while increasing separation from opponent and avoiding tight obstacle neighbors.
        improve = cur_d - nd
        score = (-nd) + 0.25 * od + 0.9 * improve - 0.4 * adj_block(nx, ny) - 0.05 * (abs(nx - tx) + abs(ny - ty))
        # Deterministic tie-break: prefer lexicographically smallest move.
        key = (-score, dx, dy, nx, ny)
        if best_s is None or key < best_s:
            best_s = key
            best = (dx, dy)
    return [int(best[0]), int(best[1])]