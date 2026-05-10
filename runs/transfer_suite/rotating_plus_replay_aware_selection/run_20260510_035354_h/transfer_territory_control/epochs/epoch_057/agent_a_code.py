def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    ax, ay = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))

    obstacles = observation.get("obstacles") or []
    oset = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            oset.add((p[0], p[1]))

    targets = observation.get("unclaimed_cells")
    if not targets:
        targets = observation.get("resources")
    if not targets:
        targets = []

    tset = []
    for p in targets:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if (x, y) not in oset:
                tset.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx + dy

    if tset:
        tx, ty = tset[0]
        bestt = dist(ax, ay, tx, ty)
        for x, y in tset[1:]:
            d = dist(ax, ay, x, y)
            if d < bestt:
                bestt, tx, ty = d, x, y
    else:
        tx, ty = ox, oy

    moves = [(-1, 0), (0, -1), (0, 0), (1, 0), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]
    bestm = (0, 0)
    bestv = None
    for dx, dy in moves:
        nx, ny = ax + dx, ay + dy
        if not inb(nx, ny) or (nx, ny) in oset:
            continue
        v = dist(nx, ny, tx, ty)
        if bestv is None or v < bestv:
            bestv, bestm = v, (dx, dy)
    return [bestm[0], bestm[1]]