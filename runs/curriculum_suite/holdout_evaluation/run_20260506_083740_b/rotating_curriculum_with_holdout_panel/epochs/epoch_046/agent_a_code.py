def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    ob = set()
    for p in obstacles:
        if p and len(p) >= 2:
            ob.add((int(p[0]), int(p[1])))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def md(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)
    def ok(x, y): return inb(x, y) and (x, y) not in ob

    best_target = None
    best_d = 10**9
    for r in resources:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if ok(rx, ry):
                d = md(sx, sy, rx, ry)
                if d < best_d or (d == best_d and (rx, ry) < best_target):
                    best_d, best_target = d, (rx, ry)

    if best_target is None:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if ok(nx, ny):
                    return [dx, dy]
        return [0, 0]

    tx, ty = best_target
    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    best = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d_self = md(nx, ny, tx, ty)
        d_opp = md(nx, ny, ox, oy)
        key = (d_self, -d_opp, dx, dy)
        if best_key is None or key < best_key:
            best_key, best = key, (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]