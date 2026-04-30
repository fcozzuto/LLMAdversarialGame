def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def ok(x, y):
        return inb(x, y) and (x, y) not in obstacles

    if not ok(sx, sy):
        for dx, dy in dirs:
            if ok(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    valid = [(dx, dy) for dx, dy in dirs if ok(sx + dx, sy + dy)]
    if not valid:
        return [0, 0]

    if resources:
        def md(a, b, c, d):
            return abs(a - c) + abs(b - d)
        target = min(resources, key=lambda t: (md(sx, sy, t[0], t[1]), t[0], t[1]))
    else:
        target = None

    best_move = None
    best_key = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        if target is not None:
            dist_t = abs(nx - target[0]) + abs(ny - target[1])
        else:
            dist_t = 0
        dist_o = abs(nx - ox) + abs(ny - oy)
        if target is not None:
            key = (dist_t, -dist_o, dx, dy)
        else:
            key = (-dist_o, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]