def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obs.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obs:
                moves.append((dx, dy))
    if not moves:
        return [0, 0]

    def cheb(a, b):
        return abs(a[0] - b[0]) if abs(a[0] - b[0]) > abs(a[1] - b[1]) else abs(a[1] - b[1])

    if res:
        scored = []
        for (rx, ry) in res:
            ds = cheb((sx, sy), (rx, ry))
            do = cheb((ox, oy), (rx, ry))
            # Prefer winning: ds <= do; strongly prefer smaller ds, then larger do.
            win = 1 if ds <= do else 0
            scored.append((win, -do, -ds, rx, ry))
        scored.sort(reverse=True)
        _, _, _, tx, ty = scored[0]
    else:
        tx, ty = w // 2, h // 2

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        d1 = cheb((nx, ny), (tx, ty))
        d2 = cheb((ox, oy), (tx, ty))
        # If we're closer to target than opponent, prioritize; otherwise block by getting closer too.
        closer = 1 if d1 <= d2 else 0
        val = (closer, -d2, -d1, dx, dy)
        if best_val is None or val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]