def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    me = observation.get("self_position") or [0, 0]
    opp = observation.get("opponent_position") or [0, 0]
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

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def legal(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    # If no resources, just approach opponent (deny space)
    if not resources:
        best = (10**9, 10**9, 10**9)
        best_move = [0, 0]
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not legal(nx, ny):
                continue
            d = man(nx, ny, ox, oy)
            cx = (w - 1) / 2
            cy = (h - 1) / 2
            cent = abs(nx - cx) + abs(ny - cy)
            key = (d, cent, (nx, ny))
            if key < best:
                best = key
                best_move = [dx, dy]
        return best_move

    # Evaluate each possible move by "winning margin" for the best target resource
    cx = (w - 1) / 2
    cy = (h - 1) / 2
    best_key = None
    best_move = [0, 0]

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue

        # Prefer stepping onto a resource immediately
        immediate = 1 if (nx, ny) in set(resources) else 0

        best_margin = -10**9
        best_tdist = 10**9
        for rx, ry in resources:
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            margin = opd - myd  # positive means we're closer than opponent to this resource
            if margin > best_margin or (margin == best_margin and myd < best_tdist):
                best_margin = margin
                best_tdist = myd

        cent_pen = abs(nx - cx) + abs(ny - cy)
        # Key: maximize margin, then immediate pickup, then minimize distance to chosen target, then prefer center
        key = (-best_margin, -immediate, best_tdist, cent_pen, (nx, ny))
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move