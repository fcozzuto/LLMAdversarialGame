def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    target = None
    if resources:
        bestd = 10**9
        for rx, ry in resources:
            d = man(sx, sy, rx, ry)
            if d < bestd:
                bestd = d
                target = (rx, ry)

    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if legal(nx, ny):
            candidates.append((nx, ny, dx, dy))
    if not candidates:
        return [0, 0]

    best = None
    bestscore = -10**18
    for nx, ny, dx, dy in candidates:
        if target:
            tx, ty = target
            score = -man(nx, ny, tx, ty)
            if (nx, ny) == target:
                score += 1000
        else:
            score = -man(nx, ny, ox, oy)
        score += -0.001 * (man(nx, ny, sx, sy))  # prefer minimal movement ties
        if score > bestscore:
            bestscore = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]