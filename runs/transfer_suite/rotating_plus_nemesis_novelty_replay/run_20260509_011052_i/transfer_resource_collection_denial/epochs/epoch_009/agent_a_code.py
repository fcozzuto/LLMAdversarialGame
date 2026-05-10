def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", (0, 0)) or (0, 0)
    op = observation.get("opponent_position", (0, 0)) or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            res.append((int(r[0]), int(r[1])))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    if res:
        best = None
        bestd = None
        targetx = targety = None
        for (rx, ry) in res:
            d = abs(rx - sx) + abs(ry - sy)
            if bestd is None or d < bestd:
                bestd, targetx, targety = d, rx, ry

        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in blocked:
                continue
            d = abs(targetx - nx) + abs(targety - ny)
            if best is None or d < bestd or (d == bestd and (dx, dy) == (0, 0)):
                best = [dx, dy]
                bestd = d
        return best if best is not None else [0, 0]

    dx = 0 if ox == sx else (1 if ox > sx else -1)
    dy = 0 if oy == sy else (1 if oy > sy else -1)
    nx, ny = sx + dx, sy + dy
    if inb(nx, ny) and (nx, ny) not in blocked:
        return [dx, dy]
    for ddx, ddy in [(dx, 0), (0, dy), (0, 0)]:
        nx, ny = sx + ddx, sy + ddy
        if inb(nx, ny) and (nx, ny) not in blocked:
            return [ddx, ddy]
    return [0, 0]