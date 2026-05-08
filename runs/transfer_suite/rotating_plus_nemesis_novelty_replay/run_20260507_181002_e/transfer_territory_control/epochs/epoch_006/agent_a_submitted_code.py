def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        if not v:
            return s
        for p in v:
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = toset(observation.get("obstacles"))
    resources = toset(observation.get("resources"))
    unclaimed = toset(observation.get("unclaimed_cells"))

    if not resources and unclaimed:
        resources = unclaimed
    if not unclaimed and resources:
        unclaimed = resources

    dirs = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    targets = list(resources if resources else unclaimed)
    if not targets:
        targets = [(ox, oy), (w - 1, h - 1)]

    # Reduce target set deterministically
    targets.sort(key=lambda p: (md(sx, sy, p[0], p[1]), p[0], p[1]))
    targets = targets[:30]

    best = None
    bestv = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        # Prefer moves that get us closer to targets than the opponent
        best_self = 10**9
        best_opp = 10**9
        for tx, ty in targets:
            d1 = md(nx, ny, tx, ty)
            if d1 < best_self:
                best_self = d1
            d2 = md(ox, oy, tx, ty)
            if d2 < best_opp:
                best_opp = d2

        # Higher is better
        val = (best_opp - best_self) * 1000 - best_self
        # Slight preference for staying near center to break ties deterministically
        cx, cy = (w - 1) // 2, (h - 1) // 2
        val -= md(nx, ny, cx, cy)

        key = (val, -dx, -dy, nx, ny)
        if best is None or key > best:
            best = key
            bestv = val

    if best is None:
        return [0, 0]

    # Recover dx, dy by re-evaluating with chosen key
    chosen = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        best_self = 10**9
        best_opp = 10**9
        for tx, ty in targets:
            d1 = md(nx, ny, tx, ty)
            if d1 < best_self:
                best_self = d1
            d2 = md(ox, oy, tx, ty)
            if d2 < best_opp:
                best_opp = d2
        val = (best_opp - best_self) * 1000 - best_self
        cx, cy = (w - 1) // 2, (h - 1) // 2
        val -= md(nx,