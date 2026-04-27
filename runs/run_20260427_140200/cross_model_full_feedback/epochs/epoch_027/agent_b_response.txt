def choose_move(observation):
    turn = int(observation.get("turn_index", 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    me = observation.get("self_position", [0, 0])
    opp = observation.get("opponent_position", [0, 0])
    sx, sy = int(me[0]), int(me[1])
    ox, oy = int(opp[0]), int(opp[1])

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    resources = []
    for r in observation.get("resources", []) or []:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if free(x, y):
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0),  (0, 0),  (1, 0),
            (-1, 1),  (0, 1),  (1, 1)]

    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    # Heuristic: move toward closest resource if safe; else move to a position that minimizes opponent proximity while staying safe.
    if resources:
        best = None
        best_score = None
        for dx, dy, nx, ny in cand:
            # distance to nearest resource
            d_res = min((abs(nx - rx) + abs(ny - ry)) for rx, ry in resources)
            # distance to opponent (prefer increasing distance)
            d_opp = abs(nx - ox) + abs(ny - oy)
            # prefer larger distance to opponent, then smaller to resource
            score = (-d_res, d_opp)
            if best_score is None or score < best_score:
                best_score = score
                best = (dx, dy, nx, ny)
        if best is not None:
            return [best[0], best[1]]

    # If no resources, move to maximize distance from opponent while staying safe
    best = None
    best_score = None
    for dx, dy, nx, ny in cand:
        d_opp = abs(nx - ox) + abs(ny - oy)
        score = (-d_opp)
        if best_score is None or score < best_score:
            best_score = score
            best = (dx, dy, nx, ny)
    if best is not None:
        return [best[0], best[1]]

    return [0, 0]