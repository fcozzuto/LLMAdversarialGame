def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))

    if not resources:
        return [0, 0]

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def cd(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0:
            ax = -ax
        ay = y1 - y2
        if ay < 0:
            ay = -ay
        return ax if ax > ay else ay

    # Prefer resources we're closer to; otherwise choose best relative advantage.
    best = None
    for rx, ry in resources:
        ds = cd(sx, sy, rx, ry)
        do = cd(ox, oy, rx, ry)
        # Strongly prefer capturing where we are strictly closer; otherwise minimize (do - ds).
        score = (0 if ds < do else 1, (do - ds), ds, rx, ry)
        if best is None or score < best[0]:
            best = (score, (rx, ry))
    tx, ty = best[1]

    # If adjacent to a resource we can take immediately, do it.
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) == (tx, ty):
            return [dx, dy]

    # Otherwise pick move that reduces distance to target, with small obstacle-safety bias.
    def obstacle_near(nx, ny):
        c = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                if (nx + ax, ny + ay) in obstacles:
                    c += 1
        return c

    best_move = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        dist = cd(nx, ny, tx, ty)
        # Prefer lower dist; break ties toward fewer neighboring obstacles; deterministic tie-break by dx,dy.
        cand = (dist, obstacle_near(nx, ny), dx, dy)
        if best_move is None or cand < best_move[0]:
            best_move = (cand, [dx, dy])
    return best_move[1]