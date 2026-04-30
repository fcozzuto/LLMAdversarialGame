def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sx, sy = observation.get("self_position") or (0, 0)
    ox, oy = observation.get("opponent_position") or (0, 0)
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            bx, by = int(p[0]), int(p[1])
            if 0 <= bx < w and 0 <= by < h:
                blocked.add((bx, by))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in blocked:
                resources.append((rx, ry))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        # Drift toward center while staying valid; tie-break by farther from opponent.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (10**9, -1, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny): continue
            d = cheb(nx, ny, cx, cy)
            do = cheb(nx, ny, ox, oy)
            cand = (d, -do, dx, dy)
            if cand < best:
                best = cand
        return [best[2], best[3]]

    # Choose best target with opponent-competition penalty.
    # Deterministic tie-breaking using fixed ordering of resources.
    scored = []
    for i, (rx, ry) in enumerate(resources):
        ds = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Encourage grabbing nearer resources; discourage if opponent much closer.
        # If ds is 0, huge priority.
        val = (1000 if ds == 0 else 0) + (30 - ds) + (do - ds)
        val -= 25 if do < ds else 0
        # Small deterministic perturbation:
        val += ((rx * 3 + ry * 5 + i) % 7) * 0.01
        scored.append((val, rx, ry, ds, do))
    scored.sort(key=lambda t: (-t[0], t[3], t[2], t[1]))
    _, tx, ty, _, _ = scored[0]

    best_move = None
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny): 
            continue
        d_now = cheb(sx, sy, tx, ty)
        d_next = cheb(nx, ny, tx, ty)
        gain = d_now - d_next  # prefer distance reduction
        # Also prefer increasing distance from opponent to avoid contesting close quarters.
        do_next = cheb(nx, ny, ox, oy)
        # Tie-break deterministic by favoring moves with smaller dx,dy lexicographically.
        cand = (-(gain * 100 + (do_next)), d_next, dx, dy, nx, ny)
        if best is None or cand < best:
            best = cand
            best_move = (dx, dy)

    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]