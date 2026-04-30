def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                resources.append((x, y))
    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        gap = od - sd  # positive => we are sooner
        # Prefer clear win: large gap, then shorter our time, then farther from opponent
        key = (gap * 1000 + (20 - sd) * 10, -sd, -(cheb(ox, oy, rx, ry) - sd))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    rx, ry = best
    dx = 0 if rx == sx else (1 if rx > sx else -1)
    dy = 0 if ry == sy else (1 if ry > sy else -1)

    cand = [(dx, dy), (dx, 0), (0, dy), (dx, -dy), (-dx, dy), (0, 0),
            (1 if rx > sx else -1, 1 if ry > sy else -1)]
    for mdx, mdy in cand:
        nx, ny = sx + mdx, sy + mdy
        if inb(nx, ny):
            return [int(mdx), int(mdy)]

    # Deterministic fallback among all deltas
    order = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    for mdx, mdy in order:
        nx, ny = sx + mdx, sy + mdy
        if inb(nx, ny):
            return [int(mdx), int(mdy)]
    return [0, 0]