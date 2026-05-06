def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def legal(x, y): return inb(x, y) and (x, y) not in blocked

    def md(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    targets = []
    for r in resources:
        if isinstance(r, dict):
            p = r.get("position")
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = p[0], p[1]
            else:
                continue
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
        else:
            continue
        if legal(x, y):
            targets.append((x, y))

    if not legal(sx, sy):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if legal(nx, ny):
                    return [dx, dy]
        return [0, 0]

    moves = [(dx, dy) for dy in (-1, 0, 1) for dx in (-1, 0, 1)]
    if not targets:
        # deterministic drift toward center
        tx, ty = (w - 1) // 2, (h - 1) // 2
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        if legal(sx + dx, sy + dy):
            return [dx, dy]
        for dxa, dya in moves:
            nx, ny = sx + dxa, sy + dya
            if legal(nx, ny):
                return [dxa, dya]
        return [0, 0]

    # pick resource where we have the best reach advantage over opponent
    best = None
    for t in targets:
        ds = md((sx, sy), t)
        do = md((ox, oy), t)
        # higher is better; slight tie-break to prefer nearer resources
        key = (do - ds, -ds, t[0], t[1])
        if best is None or key > best[0]:
            best = (key, t)
    target = best[1]

    # choose move that maximizes our immediate progress and reach advantage (one-step look)
    best_move = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        ds2 = md((nx, ny), target)
        do = md((ox, oy), target)
        val = (do - ds2, -ds2, -abs(ox - nx) - abs(oy - ny), dx, dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [best_move[0], best_move[1]] if best_move is not None else [0, 0]