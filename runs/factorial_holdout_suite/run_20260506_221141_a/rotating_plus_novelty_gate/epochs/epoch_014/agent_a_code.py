def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if not p or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if 0 <= x < w and 0 <= y < h:
            obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    targets = []
    for p in resources:
        if not p or len(p) < 2:
            continue
        x, y = int(p[0]), int(p[1])
        if inb(x, y):
            sd = abs(sx - x) + abs(sy - y)
            od = abs(ox - x) + abs(oy - y)
            targets.append((od - sd, -min(abs(sx - x), abs(sy - y)), sd, x, y))
    if not targets:
        return [0, 0]

    targets.sort(reverse=True)
    _, _, _, tx, ty = targets[0]

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        d = abs(nx - tx) + abs(ny - ty)
        val = (-d, abs(ox - nx) + abs(oy - ny), -((dx == 0 and dy == 0)))
        if best is None or val > best[0]:
            best = (val, dx, dy)
    if best is None:
        return [0, 0]
    return [int(best[1]), int(best[2])]