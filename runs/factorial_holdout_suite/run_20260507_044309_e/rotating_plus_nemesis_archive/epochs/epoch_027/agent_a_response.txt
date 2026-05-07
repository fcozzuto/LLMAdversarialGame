def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources", []) or []:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))
        except:
            pass
    if not resources:
        return [0, 0]

    def cheb(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy

    best = None
    best_key = None
    for tx, ty in resources:
        sd = cheb((sx, sy), (tx, ty))
        od = cheb((ox, oy), (tx, ty))
        win = 1 if sd < od else (0 if sd == od else -1)  # strictly sooner is best
        key = (win, -od, sd, -(tx + ty))  # avoid opponent, then closer; slight deterministic tie
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)

    tx, ty = best
    dx = 0 if tx == sx else (1 if tx > sx else -1)
    dy = 0 if ty == sy else (1 if ty > sy else -1)

    candidates = []
    for adx in (-1, 0, 1):
        for ady in (-1, 0, 1):
            nx, ny = sx + adx, sy + ady
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
                candidates.append((adx, ady))
    if not candidates:
        return [0, 0]

    def next_dist(adx, ady):
        nx, ny = sx + adx, sy + ady
        return cheb((nx, ny), (tx, ty))

    # Prefer direct step if legal, otherwise best improvement; deterministic tie by (adx, ady)
    desired = (dx, dy)
    if desired in candidates:
        candidates.sort(key=lambda a: (0 if a == desired else 1, next_dist(a[0], a[1]), a[0], a[1]))
    else:
        candidates.sort(key=lambda a: (next_dist(a[0], a[1]), a[0], a[1]))

    adx, ady = candidates[0]
    return [int(adx), int(ady)]