def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(a, b, c, d):
        da = a - c
        if da < 0:
            da = -da
        db = b - d
        if db < 0:
            db = -db
        return da if da > db else db

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    center_x, center_y = w // 2, h // 2

    best = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue

        rmin = 10**9
        for rx, ry in resources:
            d = cheb(nx, ny, rx, ry)
            if d < rmin:
                rmin = d

        d_opp = cheb(nx, ny, ox, oy)
        dist_center = cheb(nx, ny, center_x, center_y)

        val = 0
        if resources:
            val += 200 - 20 * rmin
        val += 6 * d_opp
        val -= 2 * dist_center

        if val > best_val:
            best_val = val
            best = [dx, dy]
    return best