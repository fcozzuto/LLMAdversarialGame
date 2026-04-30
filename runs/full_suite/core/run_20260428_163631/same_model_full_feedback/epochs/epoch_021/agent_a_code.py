def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obstacles.add((int(p[0]), int(p[1])))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inb(x, y) and (x, y) not in obstacles
    deltas = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    if not ok(sx, sy) or not resources:
        # Go to center-ish if no resources (avoid boundaries)
        targets = [(w // 2, h // 2), (w // 2 - 1, h // 2), (w // 2, h // 2 - 1)]
        tx, ty = targets[0]
        best = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if ok(nx, ny):
                val = (abs(nx - tx) + abs(ny - ty), abs(nx - ox) + abs(ny - oy), dx, dy)
                if best is None or val < best:
                    best = val
        if best is None:
            return [0, 0]
        return [best[2], best[3]]

    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    # Choose a target resource where we're relatively closer than opponent.
    best_target = None
    for rx, ry in resources:
        myd = man(sx, sy, rx, ry)
        opd = man(ox, oy, rx, ry)
        # Prefer resources where we are closer; otherwise deprioritize.
        rel = myd - opd
        val = (rel, myd, rx, ry)
        if best_target is None or val < best_target:
            best_target = val
    _, _, tx, ty = best_target

    # Pick move that minimizes my distance to target, while also avoiding letting opponent get much closer.
    best_move = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        myd = man(nx, ny, tx, ty)
        opd = man(ox, oy, tx, ty)
        # If opponent is already closer, mildly prioritize moves that reduce their advantage by positioning.
        opp_pos_pen = man(nx, ny, ox, oy) * 0.02
        val = (myd, (myd - opd), opp_pos_pen, abs(nx - tx) + abs(ny - ty), dx, dy)
        if best_move is None or val < best_move:
            best_move = val

    if best_move is None:
        return [0, 0]
    return [best_move[4], best_move[5]]