def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position", [0, 0]) or [0, 0]
    o = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles
    def dist(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx + dy  # stable L1-like with diagonals allowed

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if free(x, y):
                resources.append((x, y))

    if not free(sx, sy):
        sx, sy = 0, 0

    if resources and (sx, sy) in set(resources):
        return [0, 0]

    # Choose resource where we are relatively closer than opponent.
    if resources:
        best = None
        for rx, ry in resources:
            myd = dist(sx, sy, rx, ry)
            opd = dist(ox, oy, rx, ry)
            key = (opd - myd, -myd, rx, ry)  # maximize margin (we closer), then nearer, deterministic
            if best is None or key > best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]
    else:
        # No resources: move to increase chance of contact by approaching opponent's line to corner-ish.
        tx, ty = (0, h - 1) if (sx + sy) % 2 == 0 else (w - 1, 0)

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        md = dist(nx, ny, tx, ty)
        od = dist(nx, ny, ox, oy)
        # Prefer smaller distance to target; if tied, prefer farther from opponent (deny capture race).
        key = (md, -od, nx, ny)
        candidates.append((key, (dx, dy)))
    candidates.sort()
    if not candidates:
        return [0, 0]
    return [int(candidates[0][1][0]), int(candidates[0][1][1])]