def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position", [0, 0]) or [0, 0]
    o = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            legal.append((dx, dy))

    if not legal:
        return [0, 0]

    if resources:
        best = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            d = min(max(abs(nx - rx), abs(ny - ry)) for rx, ry in resources)
            cand = (d, abs(dx), abs(dy), dx, dy)
            if best is None or cand < best:
                best = cand
        return [best[3], best[4]]

    best = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d = max(abs(nx - ox), abs(ny - oy))
        cand = (-d, abs(dx), abs(dy), dx, dy)
        if best is None or cand < best:
            best = cand
    return [best[3], best[4]]