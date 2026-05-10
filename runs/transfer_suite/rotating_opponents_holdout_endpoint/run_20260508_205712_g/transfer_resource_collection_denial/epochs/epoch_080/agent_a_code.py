def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    W = int(observation.get("grid_width", 8) or 8)
    H = int(observation.get("grid_height", 8) or 8)

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < W and 0 <= y < H and (x, y) not in obs

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < W and 0 <= y < H and (x, y) not in obs:
                res.append((x, y))

    if not res:
        # fallback: move towards center-ish while staying safe
        cx, cy = (W - 1) // 2, (H - 1) // 2
        best = None
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nx, ny = sx + dx, sy + dy
                if inb(nx, ny):
                    d = abs(nx - cx) + abs(ny - cy)
                    cand = (d, nx, ny, dx, dy)
                    if best is None or cand < best:
                        best = cand
        return [int(best[3]), int(best[4])] if best else [0, 0]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    # Choose resource where we are (likely) earlier than opponent; deterministic tie-breaks.
    best_t = None
    for x, y in res:
        myd = dist(sx, sy, x, y)
        opd = dist(ox, oy, x, y)
        adv = myd - opd  # smaller is better (more likely earlier for us)
        cand = (adv, myd, x, y)
        if best_t is None or cand < best_t[0]:
            best_t = (cand, x, y)
    _, tx, ty = best_t

    # Greedy one-step: among safe neighbors, minimize manhattan to target; deterministic tie-break.
    best = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny):
                d = dist(nx, ny, tx, ty)
                # also prefer moves that increase our "lead" vs opponent to target
                my_after = dist(nx, ny, tx, ty)
                opd = dist(ox, oy, tx, ty)
                lead = my_after - opd
                cand = (d, lead, nx, ny, dx, dy)
                if best is None or cand < best:
                    best = cand
    return [int(best[4]), int(best[5])] if best else [0, 0]