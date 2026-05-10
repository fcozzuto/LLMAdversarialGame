def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    xp, yp = int(sp[0]), int(sp[1])
    op = observation.get("opponent_position") or [0, 0]
    xo, yo = int(op[0]), int(op[1])

    def to_set(key):
        s = set()
        for p in observation.get(key) or []:
            if isinstance(p, (list, tuple)) and len(p) == 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = to_set("obstacles")
    unclaimed = to_set("unclaimed_cells")
    myt = to_set("self_territory")
    opt = to_set("opponent_territory")

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    best = None
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    opt_list = list(opt)
    for dx, dy in moves:
        nx, ny = xp + dx, yp + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        score = 0.0
        if (nx, ny) in unclaimed:
            score += 60.0
        if (nx, ny) in myt:
            score += 12.0

        if (nx, ny) in opt:
            # flipping is enabled on entry: only take it if we can keep pushing
            score += 35.0
            score -= (abs(nx - xo) + abs(ny - yo)) * 1.1

        # frontier pressure: prefer cells near opponent territory and away from it when we don't enter it
        if (nx, ny) not in opt:
            score -= 0.7 * (abs(nx - xo) + abs(ny - yo))
        else:
            score += 0.2 * (abs(nx - xo) + abs(ny - yo)) * (-0.1)

        # center preference for long-term territory control
        score -= 0.06 * (abs(nx - cx) + abs(ny - cy))

        # obstacle risk: prefer destinations with more free local space
        free_neighbors = 0
        for ox in (-1, 0, 1):
            for oy in (-1, 0, 1):
                if ox == 0 and oy == 0:
                    continue
                tx, ty = nx + ox, ny + oy
                if inb(tx, ty) and (tx, ty) not in obstacles:
                    free_neighbors += 1
        score += free_neighbors * 0.8

        # tie-break determinism: slight preference for not staying still unless clearly best
        if dx == 0 and dy == 0:
            score -= 2.5

        key = (score, -(dx != 0 or dy != 0), dx, dy)
        if best is None or key > best[0]:
            best = (key, [dx, dy])

    if best is None:
        return [0, 0]
    return best[1]