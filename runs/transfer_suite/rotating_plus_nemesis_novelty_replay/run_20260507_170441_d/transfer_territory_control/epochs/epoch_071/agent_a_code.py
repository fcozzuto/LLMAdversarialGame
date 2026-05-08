def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in (observation.get("obstacles") or []):
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    resources = observation.get("resources") or []
    res = set()
    for p in resources:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                res.add((x, y))
        except:
            pass

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    best_move = [0, 0]
    best_val = -10**18

    cx, cy = (w - 1) // 2, (h - 1) // 2

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in blocked:
            continue

        val = 0
        d_op = man(nx, ny, ox, oy)
        val += 30 * d_op

        if res:
            d_min = min(man(nx, ny, rx, ry) for (rx, ry) in res)
            val += 800 - 40 * d_min
            if (nx, ny) in res:
                val += 5000
        else:
            val += 20 * (-(man(nx, ny, cx, cy)))

        if dx == 0 and dy == 0:
            val -= 15

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move