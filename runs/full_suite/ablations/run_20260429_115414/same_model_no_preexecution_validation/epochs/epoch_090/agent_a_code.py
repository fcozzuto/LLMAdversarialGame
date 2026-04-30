def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

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
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def neigh_steps(x, y):
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    yield 0, 0, x, y
                else:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                        yield dx, dy, nx, ny

    # Target selection: prefer resources we can reach sooner, but also those opponent is less able to reach soon.
    # Deterministic tie-break: lexicographic on coordinates.
    best = None
    for rx, ry in resources:
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Encourage winning contests; also slight preference for closer resources.
        score = (do - ds) * 10 - ds
        if best is None or score > best[0] or (score == best[0] and (rx, ry) < best[1]):
            best = (score, (rx, ry))
    _, (tx, ty) = best

    # Choose the move that most reduces distance to target; if tied, push away from opponent's distance to same target;
    # if still tied, avoid moving adjacent to obstacles; deterministic tie-break by dx,dy order.
    cur_ds = cheb(sx, sy, tx, ty)
    cur_do = cheb(ox, oy, tx, ty)

    def adj_obst_pen(x, y):
        pen = 0
        for oy2 in (-1, 0, 1):
            for ox2 in (-1, 0, 1):
                nx, ny = x + ox2, y + oy2
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) in obstacles:
                    pen += 1
        return pen

    best_move = (0, 0)
    best_key = None
    # Deterministic iteration order: dx then dy for stable tie-breaking
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
                continue
            nds = cheb(nx, ny, tx, ty)
            # simulate opponent not possible; use current do as proxy
            opp_pressure = cur_do - cheb(ox, oy, tx, ty)  # always 0; kept for structure
            # primary: minimize distance, secondary: increase opponent's relative disadvantage, tertiary: obstacle clearance
            rel = (cur_do - nds)
            pen = adj_obst_pen(nx, ny)
            key = (-(nds), -(rel), pen, dx, dy)
            if best_key is None or key > best_key:
                best_key = key
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]