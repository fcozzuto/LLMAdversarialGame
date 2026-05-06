def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    ob = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                ob.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in ob

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    res = []
    for r in resources:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if valid(x, y):
                res.append((x, y))

    if res:
        tx, ty = min(res, key=lambda t: (dist(sx, sy, t[0], t[1]), t[0], t[1]))
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        before = dist(sx, sy, tx, ty)
        after = dist(nx, ny, tx, ty)
        opp = dist(nx, ny, ox, oy)
        # Prefer closer to target; tie-break by farther from opponent; then deterministic by move order.
        cand = (after - before, -opp, abs(dx) + abs(dy), dx, dy)
        if best is None or cand < best[0]:
            best = (cand, [dx, dy])

    if best is None:
        return [0, 0]
    return best[1]