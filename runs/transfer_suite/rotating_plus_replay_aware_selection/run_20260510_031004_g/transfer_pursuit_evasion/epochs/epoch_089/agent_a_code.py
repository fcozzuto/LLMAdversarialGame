def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    self_role = (observation.get("self_role", "") or "").lower()
    opp_role = (observation.get("opponent_role", "") or "").lower()
    self_is_pursuer = ("purs" in self_role) or ("purs" in opp_role)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
        except Exception:
            pass

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            candidates.append((nx, ny, dx, dy))

    if not candidates:
        return [0, 0]

    def cheb_dist(x, y):
        dx = abs(ox - x)
        dy = abs(oy - y)
        return dx if dx > dy else dy

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best = None
    for nx, ny, dx, dy in candidates:
        d = cheb_dist(nx, ny)
        # tie-break: also prefer positions that keep options (evader) or avoid dead-ends (pursuer)
        deg = 0
        for adx, ady in moves:
            tx, ty = nx + adx, ny + ady
            if inb(tx, ty) and (tx, ty) not in obstacles:
                deg += 1
        center_bias = -abs(nx - cx) - abs(ny - cy)
        if self_is_pursuer:
            key = (d, -deg, -center_bias, nx, ny)
        else:
            key = (-d, -deg, center_bias, nx, ny)
        if best is None or key < best[0]:
            best = (key, dx, dy)

    return [int(best[1]), int(best[2])]