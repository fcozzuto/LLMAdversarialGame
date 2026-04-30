def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    tx, ty = (w - 1) // 2, (h - 1) // 2
    if resources:
        best = None
        for (rx, ry) in resources:
            ds = cheb(sx, sy, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # Prefer targets where we can beat opponent and also closer to finish
            score = (do - ds) * 100 - ds
            cand = (score, -rx, -ry, ds, do)
            if best is None or cand > best:
                best = cand
                tx, ty = rx, ry

    # Choose among our legal moves by maximizing improvement toward target,
    # while penalizing moves that bring us closer to opponent relative to target.
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        ds2 = cheb(nx, ny, tx, ty)
        ds1 = cheb(sx, sy, tx, ty)
        do = cheb(ox, oy, tx, ty)
        # primary: reduce distance to chosen target; secondary: keep advantage vs opponent
        val = (ds1 - ds2) * 1000 + (do - ds2) * 10 - cheb(nx, ny, ox, oy)
        cand = (val, -dx, -dy)
        if best_val is None or cand > best_val:
            best_val = cand
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]