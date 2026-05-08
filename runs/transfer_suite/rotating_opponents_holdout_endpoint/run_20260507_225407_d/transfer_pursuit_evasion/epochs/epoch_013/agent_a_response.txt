def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p is None:
            continue
        x, y = p
        obstacles.add((int(x), int(y)))

    self_role = (observation.get("self_role", "") or "")
    pursuer = ("purs" in self_role.lower())

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not valid(sx, sy):
        return [0, 0]

    if pursuer:
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            key = (d, dx * dx + dy * dy)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        if best is None:
            return [0, 0]
        return best[1]

    corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
    accessible = [c for c in corners if valid(c[0], c[1])]
    if accessible:
        tx, ty = max(accessible, key=lambda c: (cheb(c[0], c[1], ox, oy), c[0], c[1]))
    else:
        tx, ty = (0, 0) if (ox + oy) <= (w - 1 + h - 1 - ox + h - 1 - oy) else (w - 1, h - 1)

    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dist_away = cheb(nx, ny, ox, oy)
        toward = cheb(nx, ny, tx, ty)
        key = (-dist_away, toward, dx * dx + dy * dy)
        if best is None or key < best[0]:
            best = (key, [dx, dy])
    if best is None:
        return [0, 0]
    return best[1]