def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = []
    for r in (observation.get("resources", []) or []):
        q = None
        if isinstance(r, dict):
            q = r.get("position", None)
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            q = r
        if isinstance(q, (list, tuple)) and len(q) >= 2:
            x, y = int(q[0]), int(q[1])
            if inb(x, y):
                resources.append((x, y))

    if resources:
        tx, ty = min(resources, key=lambda t: cheb(sx, sy, t[0], t[1]))
    else:
        tx, ty = ox, oy

    best = None
    bestd = 10**9
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = cheb(nx, ny, tx, ty)
            if d < bestd or (d == bestd and (dx, dy) < best):
                bestd = d
                best = (dx, dy)

    if best is None:
        return [0, 0]
    return [best[0], best[1]]