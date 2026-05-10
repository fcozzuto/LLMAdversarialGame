def choose_move(observation):
    W = int(observation.get("grid_width", 0) or 0)
    H = int(observation.get("grid_height", 0) or 0)
    if W <= 0 or H <= 0:
        return [0, 0]

    sp = observation.get("self_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for c in obstacles:
        if isinstance(c, (list, tuple)) and len(c) >= 2:
            obs.add((int(c[0]), int(c[1])))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    ot = observation.get("opponent_territory", []) or []
    op_set = set()
    for c in ot:
        if isinstance(c, (list, tuple)) and len(c) >= 2:
            op_set.add((int(c[0]), int(c[1])))

    def manh(x, y, tx, ty):
        return abs(x - tx) + abs(y - ty)

    target = None
    unclaimed = observation.get("unclaimed_cells", []) or []
    frontier = []
    for c in unclaimed:
        if isinstance(c, (list, tuple)) and len(c) >= 2:
            x, y = int(c[0]), int(c[1])
            if (x, y) in obs or not inb(x, y):
                continue
            adj = False
            for ddx, ddy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                if (x + ddx, y + ddy) in op_set:
                    adj = True
                    break
            if adj:
                frontier.append((x, y))

    if frontier:
        target = min(frontier, key=lambda p: (manh(sx, sy, p[0], p[1]), p[1], p[0]))
    else:
        res = observation.get("resources", []) or []
        resources = []
        for c in res:
            if isinstance(c, (list, tuple)) and len(c) >= 2:
                x, y = int(c[0]), int(c[1])
                if (x, y) in obs or not inb(x, y):
                    continue
                resources.append((x, y))
        if resources:
            target = min(resources, key=lambda p: (manh(sx, sy, p[0], p[1]), p[1], p[0]))
        else:
            op = observation.get("opponent_position", [sx, sy]) or [sx, sy]
            target = (int(op[0]), int(op[1]))

    tx, ty = target
    best = [0, 0]
    bestd = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        d = manh(nx, ny, tx, ty)
        if bestd is None or d < bestd or (d == bestd and (dy, dx) < (best[1], best[0])):