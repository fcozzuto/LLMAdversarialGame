def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = abs(x1 - x2)
        dy = abs(y1 - y2)
        return dx if dx > dy else dy

    best = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        margin = od - sd  # positive means we arrive earlier (or tie favored by later sort)
        key = (-margin, sd, od, rx + ry, rx, ry)
        if best is None or key < best[0]:
            best = (key, rx, ry)

    tx, ty = best[1], best[2]

    candidates = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                candidates.append((dx, dy, cheb(nx, ny, tx, ty)))
    if not candidates:
        return [0, 0]

    # Prefer reducing distance; break ties by also moving away from opponent a bit to avoid shadowing.
    bestm = None
    for dx, dy, dist in candidates:
        nx, ny = sx + dx, sy + dy
        opd = cheb(nx, ny, ox, oy)
        key = (dist, -opd, dx, dy)
        if bestm is None or key < bestm[0]:
            bestm = (key, dx, dy)
    return [bestm[1], bestm[2]]