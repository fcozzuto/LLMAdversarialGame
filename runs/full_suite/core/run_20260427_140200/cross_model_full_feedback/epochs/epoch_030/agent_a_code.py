def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position", [0, 0]) or [0, 0]
    opp = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    best = None
    if resources:
        for dx, dy, nx, ny in candidates:
            dres = min(abs(nx - rx) + abs(ny - ry) for rx, ry in resources)
            dopp = abs(nx - ox) + abs(ny - oy)
            score = (-dres, -dopp, -abs(dx) - abs(dy))
            if best is None or score > best[0]:
                best = (score, dx, dy)
    else:
        for dx, dy, nx, ny in candidates:
            d_opp = abs(nx - ox) + abs(ny - oy)
            score = (d_opp, -abs(dx) - abs(dy), -nx - ny)
            if best is None or score > best[0]:
                best = (score, dx, dy)

    return [int(best[1]), int(best[2])]