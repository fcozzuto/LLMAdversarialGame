def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked
    def cheb(a, b):
        return abs(a[0] - b[0]) if abs(a[0] - b[0]) > abs(a[1] - b[1]) else abs(a[1] - b[1])
    def step_towards(tx, ty):
        best = (10**9, 10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = cheb((nx, ny), (tx, ty))
            # tie-break deterministically by move preference then position-less stable ordering
            key = (d, abs(dx) + abs(dy), dx, dy)
            if key < best:
                best = (key[0], key[1], key[2], key[3])
        return [best[2], best[3]] if best[3] or best[2] or best[0] != 10**9 else [0, 0]

    if not resources:
        cx, cy = w // 2, h // 2
        return step_towards(cx, cy)

    best = None
    for r in resources:
        if not (isinstance(r, (list, tuple)) and len(r) >= 2):
            continue
        tx, ty = r[0], r[1]
        if not (isinstance(tx, int) and isinstance(ty, int)):
            continue
        if not inb(sx, sy):
            pass
        myd = cheb((sx, sy), (tx, ty))
        opd = cheb((ox, oy), (tx, ty))
        # Prefer resources we can reach earlier; otherwise still reduce our disadvantage.
        # Small lexicographic tie-break on resource coordinates for determinism.
        key = (myd - opd, myd, tx, ty)
        if best is None or key < best[0]:
            best = (key, tx, ty)

    _, tx, ty = best
    return step_towards(tx, ty)