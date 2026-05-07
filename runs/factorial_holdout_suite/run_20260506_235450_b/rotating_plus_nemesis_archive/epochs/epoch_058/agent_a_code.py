def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def md(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    if resources:
        best = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            if (rx, ry) in obs:
                continue
            dme = md(sx, sy, rx, ry)
            do = md(ox, oy, rx, ry)
            # Prefer resources where we are closer than opponent; then nearer to us.
            val = (dme - do, dme, (rx + ry) % 2, rx, ry)
            if best is None or val < best[0]:
                best = (val, (rx, ry))
        target = best[1] if best else None
    else:
        target = None

    if target is None:
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        bestc = None
        for cx, cy in corners:
            v = (md(sx, sy, cx, cy) - md(ox, oy, cx, cy), md(sx, sy, cx, cy), cx, cy)
            if bestc is None or v < bestc:
                bestc = v
                target = (cx, cy)

    tx, ty = target
    bestm = (0, 0)
    bestv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        dme2 = md(nx, ny, tx, ty)
        do2 = md(ox, oy, tx, ty)
        # Also mildly prefer moves that increase opponent's difficulty (when ties occur).
        v = (dme2 - do2, dme2, (dx, dy))
        if bestv is None or v < bestv:
            bestv = v
            bestm = (dx, dy)
    return [int(bestm[0]), int(bestm[1])]