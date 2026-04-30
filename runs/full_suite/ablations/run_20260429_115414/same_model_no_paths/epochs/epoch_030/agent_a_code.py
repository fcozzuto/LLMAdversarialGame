def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obs = set()
    for b in observation.get("obstacles") or []:
        if b is not None and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obs.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r is not None and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obs:
                resources.append((rx, ry))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    if resources:
        for rx, ry in resources:
            d = abs(rx - sx)
            e = abs(ry - sy)
            dist = d if d > e else e
            if best is None or dist < best[0] or (dist == best[0] and (ry < best[2] or (ry == best[2] and rx < best[1]))):
                best = (dist, rx, ry)
    else:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (0, cx, cy)

    _, tx, ty = best
    options = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs:
            options.append((dx, dy, nx, ny))

    if not options:
        return [0, 0]

    def dist_to_target(nx, ny):
        dx = nx - tx
        if dx < 0:
            dx = -dx
        dy = ny - ty
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def dist_to_opponent(nx, ny):
        dx = nx - ox
        if dx < 0:
            dx = -dx
        dy = ny - oy
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    scored = []
    for dx, dy, nx, ny in options:
        scored.append((dist_to_target(nx, ny), -dist_to_opponent(nx, ny), dx, dy, nx, ny))
    scored.sort()
    return [int(scored[0][2]), int(scored[0][3])]