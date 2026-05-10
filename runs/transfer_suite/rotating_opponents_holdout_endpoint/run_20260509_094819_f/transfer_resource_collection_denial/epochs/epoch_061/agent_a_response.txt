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

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Heuristic: prioritize resources where we are closer (race), otherwise still grab high-value lines
    # Deterministic tie-breaking by coordinates.
    best = None
    bestk = None
    for x, y in resources:
        sd = cheb(x, y, sx, sy)
        od = cheb(x, y, ox, oy)
        race = od - sd  # positive favors us
        key = (race, -sd, -abs(ox - x) - abs(oy - y), -x, -y, x, y)
        if bestk is None or key > bestk:
            bestk = key
            best = (x, y)

    tx, ty = best

    dirs = []
    if tx == sx and ty == sy:
        return [0, 0]
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                # prefer moves that reduce Chebyshev distance to target
                nd = cheb(nx, ny, tx, ty)
                cd = cheb(sx, sy, tx, ty)
                dirs.append((-(nd - cd), abs((tx - nx)) + abs((ty - ny)), dx, dy))
    if not dirs:
        return [0, 0]
    dirs.sort()
    # deterministic: if multiple, fixed sort by tuple order above
    return [int(dirs[-1][2]), int(dirs[-1][3])]