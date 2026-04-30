def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def sign(v):
        return -1 if v < 0 else (1 if v > 0 else 0)

    if resources:
        best_t = None
        best_s = None
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Prefer resources where we are not behind; prioritize closeness when we are ahead.
            s = (opd - myd) * 10 - myd
            if opd < myd:
                s -= 20  # actively avoid resources opponent is closer to
            if best_s is None or s > best_s or (s == best_s and (rx, ry) < best_t):
                best_s = s
                best_t = (rx, ry)
        tx, ty = best_t
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    dx = sign(tx - sx)
    dy = sign(ty - sy)

    # Try up to 9 neighbor deltas, deterministically preferring those that reduce distance to target.
    deltas = []
    for mx in (-1, 0, 1):
        for my in (-1, 0, 1):
            nx, ny = sx + mx, sy + my
            if inb(nx, ny):
                dcur = cheb(nx, ny, tx, ty)
                deltas.append((dcur, abs(mx - dx) + abs(my - dy), mx, my))
    if deltas:
        deltas.sort(key=lambda t: (t[0], t[1], t[2], t[3]))
        return [int(deltas[0][2]), int(deltas[0][3])]

    return [0, 0]