def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    if not free(sx, sy):
        for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
            if free(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    if not resources:
        best = None
        bestv = -10**9
        for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            d = abs(nx - ox) + abs(ny - oy)
            v = d
            if v > bestv:
                bestv, best = v, (dx, dy)
        return [best[0], best[1]] if best else [0, 0]

    best = None
    bestv = -10**18
    for dx, dy in [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        if resources:
            md = min(abs(nx - rx) + abs(ny - ry) for rx, ry in resources)
        else:
            md = 10**9
        oppd = abs(nx - ox) + abs(ny - oy)
        v = -md * 10 - (0 if (nx, ny) == (ox, oy) else oppd)
        if v > bestv:
            bestv, best = v, (dx, dy)

    return [best[0], best[1]] if best else [0, 0]