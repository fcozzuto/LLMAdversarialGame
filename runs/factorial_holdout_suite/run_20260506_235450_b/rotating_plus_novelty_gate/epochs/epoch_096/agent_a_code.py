def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sp = observation.get("self_position", [0, 0])
    op = observation.get("opponent_position", [0, 0])
    sx, sy = sp[0], sp[1]
    ox, oy = op[0], op[1]

    obstacles = observation.get("obstacles", []) or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        dy = y1 - y2
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy

    resources = observation.get("resources", []) or []
    rs = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            tx, ty = r[0], r[1]
            if isinstance(tx, int) and isinstance(ty, int) and inb(tx, ty):
                rs.append((tx, ty))
    if not rs:
        dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                return [dx, dy]
        return [0, 0]

    best = None
    best_score = None
    for tx, ty in rs:
        ds = man(sx, sy, tx, ty)
        do = man(ox, oy, tx, ty)
        # If behind, prioritize closing the gap to contest; if ahead, go for it.
        gap = do - ds
        score = (0 if gap < 0 else 1, -gap, ds, tx, ty)
        if best_score is None or score > best_score:
            best_score = score
            best = (tx, ty)

    tx, ty = best
    candidates = [(1, 0), (-1, 0), (0, 1), (0, -1), (0, 0)]
    best_d = None
    best_h = None
    for dx, dy in candidates:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        h = man(nx, ny, tx, ty)
        # Tie-break by opponent distance improvement to reduce being out-raced.
        ho = man(nx, ny, ox, oy)
        key = (-h, ho, dx, dy)
        if best_h is None or key > best_h:
            best_h = key
            best_d = (dx, dy)
    if best_d is None:
        return [0, 0]
    return [int(best_d[0]), int(best_d[1])]