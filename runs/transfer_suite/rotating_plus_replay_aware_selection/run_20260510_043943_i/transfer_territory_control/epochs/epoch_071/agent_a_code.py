def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or (0, 0)
    op = observation.get("opponent_position") or (0, 0)
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    unclaimed = observation.get("unclaimed_cells") or []
    resources = observation.get("resources") or []
    candidates = []

    for r in resources:
        if r and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if ok(x, y):
                candidates.append((x, y))
    if not candidates:
        for c in unclaimed:
            if c and len(c) >= 2:
                x, y = int(c[0]), int(c[1])
                if ok(x, y):
                    candidates.append((x, y))

    # If still nothing, try to move toward opponent to deny space.
    if not candidates:
        candidates = [(ox, oy), (w // 2, h // 2), (0, 0), (w - 1, h - 1), (w // 2, 0), (0, h // 2), (w - 1, h // 2), (w // 2, h - 1)]
        candidates = [(x, y) for (x, y) in candidates if ok(x, y)]

    def score_cell(x, y):
        ds = (x - sx) * (x - sx) + (y - sy) * (y - sy)
        do = (x - ox) * (x - ox) + (y - oy) * (y - oy)
        # Prefer cells we can reach sooner than opponent; lightly prefer toward center.
        center = (x - w // 2) * (x - w // 2) + (y - h // 2) * (y - h // 2)
        return (ds - do, center, abs(x - sx) + abs(y - sy), x, y)

    targets = candidates
    best = None
    for x, y in targets:
        s = score_cell(x, y)
        if best is None or s < best[0]:
            best = (s, (x, y))
    tx, ty = best[1] if best else (sx, sy)

    # Choose step that decreases distance to target, with deterministic tie-breaker and obstacle safety.
    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        d = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        # Also deny opponent by preferring moves that increase our lead vs opponent.
        lead = ((nx - sx) * (nx - sx) + (ny - sy) * (ny - sy),)  # always 0 or 1 step; keeps determinism
        opp_d = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
        v = (d, -opp_d, dx, dy)
        if best_val is None or v < best_val:
            best_val = v
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]