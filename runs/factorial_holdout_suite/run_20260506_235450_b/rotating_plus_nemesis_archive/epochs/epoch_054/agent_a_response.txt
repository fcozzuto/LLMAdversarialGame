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

    def man(a, b, c, d):
        x = a - c
        if x < 0:
            x = -x
        y = b - d
        if y < 0:
            y = -y
        return x + y

    if not resources:
        tx, ty = ox, oy
    else:
        best = None
        best_v = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            sd = man(sx, sy, rx, ry)
            od = man(ox, oy, rx, ry)
            v = (od - sd, -sd, -rx, -ry)
            if best_v is None or v > best_v:
                best_v = v
                best = (rx, ry)
        tx, ty = best
        if (sx, sy) == (tx, ty):
            return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_m = None
    best_s = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sd2 = man(nx, ny, tx, ty)
        od2 = man(ox, oy, tx, ty)
        score = (-sd2, od2, abs(nx - ox) + abs(ny - oy), nx, ny)
        if best_s is None or score > best_s:
            best_s = score
            best_m = (dx, dy)

    if best_m is None:
        return [0, 0]
    return [int(best_m[0]), int(best_m[1])]