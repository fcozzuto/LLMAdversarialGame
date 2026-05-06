def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    resources = observation.get("resources", []) or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obst

    def man(ax, ay, bx, by):
        return abs(ax - bx) + abs(ay - by)

    if not inb(sx, sy):
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
        return [0, 0]

    if not res:
        # deterministic safe drift toward center-ish
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = man(nx, ny, tx, ty)
            cand = (d, abs(nx - ox) + abs(ny - oy), dx, dy)
            if best is None or cand < best:
                best = cand
        return [best[2], best[3]] if best else [0, 0]

    # Choose contested/denied resource: prefer where opponent is close but we can arrive as fast or faster
    best_cell = None
    best_key = None
    for x, y in res:
        sd = man(sx, sy, x, y)
        od = man(ox, oy, x, y)
        # primary: opp lead by us (od - sd); secondary: closer overall (smaller min dist)
        lead = od - sd
        mind = sd if sd < od else od
        key = (-lead, mind, sd, x, y)  # minimize -lead => maximize lead
        if best_key is None or key < best_key:
            best_key, best_cell = key, (x, y)

    tx, ty = best_cell
    # move greedily toward target, but if blocked choose best available
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        sd = man(nx, ny, tx, ty)
        od = man(ox, oy, tx, ty)
        # prefer reducing our distance, while keeping pressure if opponent is also near
        key = (sd, -od + sd, abs(nx - ox) + abs(ny - oy), dx, dy)
        if best is None or key < best:
            best = key
    return [best[3], best[4]] if best else [0, 0]