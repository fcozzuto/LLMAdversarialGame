def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0] or 0), int(sp[1] or 0)
    ox, oy = int(op[0] or (w - 1)), int(op[1] or (h - 1))

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = set()
    for p in resources:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obs:
                res.add((x, y))

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            legal.append((dx, dy))

    if not legal:
        return [0, 0]

    if res:
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            dmy = min(abs(nx - rx) + abs(ny - ry) for (rx, ry) in res)
            do = abs(nx - ox) + abs(ny - oy)
            score = (dmy, do)  # go to closest resource, while keeping away from opponent slightly
            if best is None or score < best[0]:
                best = (score, (dx, dy))
        return [int(best[1][0]), int(best[1][1])]

    cx, cy = w // 2, h // 2
    best = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        score = (abs(nx - cx) + abs(ny - cy), abs(nx - ox) + abs(ny - oy))
        if best is None or score < best[0]:
            best = (score, (dx, dy))
    return [int(best[1][0]), int(best[1][1])]