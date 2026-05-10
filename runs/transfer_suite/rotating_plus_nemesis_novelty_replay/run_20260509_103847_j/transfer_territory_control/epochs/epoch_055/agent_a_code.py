def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    sx, sy = int(sx), int(sy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    op = observation.get("opponent_position") or [w - 1, h - 1]
    ox, oy = int(op[0]), int(op[1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    candidates = []
    for key in ("resources", "unclaimed_cells", "opponent_territory"):
        if candidates:
            break
        for p in observation.get(key) or []:
            if len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if inb(x, y) and (x, y) != (sx, sy):
                    candidates.append((x, y))

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    if candidates:
        tx, ty = min(candidates, key=lambda p: (man(sx, sy, p[0], p[1]) - 0.1 * man(ox, oy, p[0], p[1]), -p[0], -p[1]))
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        if not inb(tx, ty):
            tx, ty = sx, sy

    best = None
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d_self = man(nx, ny, tx, ty)
        d_op = man(nx, ny, ox, oy)
        val = (d_self, -d_op, abs(dx) + abs(dy))
        if best_val is None or val < best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        if inb(sx, sy):
            return [0, 0]
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
        return [0, 0]

    return [int(best[0]), int(best[1])]