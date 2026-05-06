def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    obstacles = observation.get("obstacles", []) or []
    resources = observation.get("resources", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            blocked.add((p[0], p[1]))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def legal(x, y): return inb(x, y) and (x, y) not in blocked
    def md(a, b): return abs(a[0] - b[0]) + abs(a[1] - b[1])

    rpos = []
    for r in resources:
        if isinstance(r, dict):
            p = r.get("position")
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                x, y = p[0], p[1]
                if legal(x, y): rpos.append((x, y))
        elif isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if legal(x, y): rpos.append((x, y))

    if not legal(sx, sy):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if legal(sx + dx, sy + dy):
                    return [dx, dy]
        return [0, 0]

    if not rpos:
        return [0, 0]

    # Pick a contested target first (our distance <= opponent distance), then maximize advantage.
    best = None
    for t in rpos:
        ds = md((sx, sy), t)
        do = md((ox, oy), t)
        contested = ds <= do
        key = (0 if contested else 1, ds - do, ds)  # smaller is better
        if best is None or key < best[0]:
            best = (key, t)
    t = best[1]

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    bestm = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        ns = md((nx, ny), t)
        # Blocking: also consider how much this move worsens our ability relative to opponent.
        nos = md((ox, oy), t)
        key = (ns, (ns - nos), abs(nx - ox) + abs(ny - oy), dx * dx + dy * dy)
        if bestm is None or key < bestm[0]:
            bestm = (key, [dx, dy])
    return bestm[1] if bestm is not None else [0, 0]