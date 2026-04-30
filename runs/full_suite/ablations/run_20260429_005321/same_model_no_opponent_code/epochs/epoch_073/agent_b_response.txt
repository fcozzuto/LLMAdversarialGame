def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in (observation.get("obstacles", []) or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in (observation.get("resources", []) or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def d2(ax, ay, bx, by):
        dx, dy = ax - bx, ay - by
        return dx * dx + dy * dy

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # If no resources, just drift toward center deterministically.
    if not resources:
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        best_key = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            score = -((nx - tx) * (nx - tx) + (ny - ty) * (ny - ty))
            key = (score, dx, dy)
            if best_key is None or key > best_key:
                best_key = key
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    best = (0, 0)
    best_key = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        # Evaluate by targeting resources where we gain most closeness advantage.
        local_best = None
        for rx, ry in resources:
            my = d2(nx, ny, rx, ry)
            opd = d2(ox, oy, rx, ry)
            adv = opd - my  # positive: we are closer than opponent after move
            # Encourage taking immediate proximity too, with diminishing returns.
            score = adv * 4 - my * 0.5
            # Small deterministic bias to avoid ties.
            key = (score, -rx, -ry)
            if local_best is None or key > local_best:
                local_best = key

        # If we can tie resources, prefer moves that keep options (smaller my dist to best resource).
        score_best = local_best[0]
        key2 = (score_best, -dx, -dy)
        if best_key is None or key2 > best_key:
            best_key = key2
            best = (dx, dy)

    return [int(best[0]), int(best[1])]