def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    cx, cy = (w - 1) // 2, (h - 1) // 2

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    if (sx, sy) in obstacles or not inb(sx, sy):
        candidates = [(dx, dy) for dx, dy in deltas if inb(sx + dx, sy + dy) and (sx + dx, sy + dy) not in obstacles]
        return list(candidates[0]) if candidates else [0, 0]

    def score_move(dx, dy, tx, ty):
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            return 10**9
        d_self = abs(nx - tx) + abs(ny - ty)
        d_opp = abs(nx - ox) + abs(ny - oy)
        return d_self - 0.1 * d_opp

    target = resources[0] if resources else (cx, cy)
    if resources:
        best_d = 10**9
        for x, y in resources:
            d = abs(x - sx) + abs(y - sy)
            if d < best_d:
                best_d = d
                target = (x, y)
    else:
        target = (cx, cy)

    tx, ty = target
    best = (10**9, 0, 0)
    for dx, dy in deltas:
        s = score_move(dx, dy, tx, ty)
        if s < best[0]:
            best = (s, dx, dy)

    return [int(best[1]), int(best[2])]