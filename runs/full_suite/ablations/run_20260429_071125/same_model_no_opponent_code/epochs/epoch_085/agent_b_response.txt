def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    turn = int(observation.get("turn_index", 0) or 0)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def man(x1, y1, x2, y2): return abs(x1 - x2) + abs(y1 - y2)

    rem = int(observation.get("remaining_resource_count", len(resources)) or len(resources))
    # Choose a target resource that we can reach earlier than opponent.
    best = None
    for (x, y) in resources:
        ds = man(sx, sy, x, y)
        do = man(ox, oy, x, y)
        # Slight deterministic bias to break ties and to adapt as game progresses.
        progress = 1.0 - (rem / max(1.0, float(len(resources))))
        v = (do - ds) + (0.15 + 0.35 * progress) * (-ds) + 0.01 * ((x + y) % 7)
        key = (v, -ds, -(x + y), x, y)
        if best is None or key > best[0]:
            best = (key, (x, y))
    tx, ty = best[1]

    moves = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    # Deterministic tie-breaker ordering: stay last by favoring moves with smaller dx/dy lexicographically.
    moves.sort(key=lambda t: (t[0], t[1]))

    bestm = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue
        # Prefer approaching target, avoid becoming "closer to opponent" than needed.
        dsn = man(nx, ny, tx, ty)
        don = man(ox, oy, tx, ty)
        my_adv = don - dsn
        # Penalize stepping away; add small penalty if target is far.
        score = my_adv * 2.0 - dsn * 0.08 - (man(nx, ny, ox, oy) * 0.01)
        key = (score, -dsn, dx, dy)
        if bestm is None or key > bestm[0]:
            bestm = (key, dx, dy)

    if bestm is None:
        return [0, 0]
    return [int(bestm[1]), int(bestm[2])]