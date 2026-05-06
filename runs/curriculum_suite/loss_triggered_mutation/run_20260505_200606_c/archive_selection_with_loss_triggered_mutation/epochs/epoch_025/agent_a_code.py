def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    rem = observation.get("remaining_resource_count", None)

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not resources:
        # fallback: move away or stay if blocked
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = abs(nx - ox) + abs(ny - oy)
            key = (d, -dx, -dy)
            if best is None or key > best[0]:
                best = (key, [dx, dy])
        return best[1] if best is not None else [0, 0]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # pick resource that we can reach sooner than opponent (approx, ignoring obstacles)
    best_r = None
    best_k = None
    for r in resources:
        if r is None or len(r) < 2:
            continue
        rx, ry = int(r[0]), int(r[1])
        if not inb(rx, ry):
            continue
        ds = man(sx, sy, rx, ry)
        do = man(ox, oy, rx, ry)
        # prefer resources when close; if tie, prefer those closer to us
        k = (do - ds, -ds, -rx, -ry)
        if best_k is None or k > best_k:
            best_k = k
            best_r = (rx, ry)

    tx, ty = best_r if best_r is not None else (sx, sy)

    # evaluate one-step moves toward target while discouraging letting opponent gain
    best_move = [0, 0]
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ns = man(nx, ny, tx, ty)
        os = man(ox, oy, tx, ty)
        # assume opponent will also move one step (approx) by reducing their distance by 1
        gain = (os - 1) - ns
        # avoid getting closer to opponent when we are not improving
        avoid = -man(nx, ny, ox, oy)
        # light tie-breakers
        k = (gain, -ns, avoid, -dx, -dy)
        if best_val is None or k > best_val:
            best_val = k
            best_move = [dx, dy]
    return best_move if best_val is not None else [0, 0]