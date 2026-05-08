def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obs = set()
    for p in observation.get("obstacles") or []:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obs

    cand = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
    targets = []

    for p in (observation.get("resources") or []):
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                targets.append((x, y))
    if not targets:
        for p in (observation.get("unclaimed_cells") or []):
            if p is not None and len(p) >= 2:
                x, y = int(p[0]), int(p[1])
                if inb(x, y):
                    targets.append((x, y))
    if not targets:
        # fallback: push toward opponent
        targets = [(ox, oy)]

    # Precompute for determinism: nearest target distance (Manhattan)
    best = None
    best_key = None

    def man(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    order_bias = {(0, 0): 0, (1, 0): 1, (-1, 0): 2, (0, 1): 3, (0, -1): 4}

    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        mdist = min(mant for mant in [man(nx, ny, tx, ty) for (tx, ty) in targets]) if targets else 0
        # Slightly prefer moving away from obstacles only implicitly via feasibility; tie-break deterministically.
        key = (mdist, order_bias[(dx, dy)])
        if best_key is None or key < best_key:
            best_key = key
            best = [dx, dy]

    if best is None:
        return [0, 0]
    return best