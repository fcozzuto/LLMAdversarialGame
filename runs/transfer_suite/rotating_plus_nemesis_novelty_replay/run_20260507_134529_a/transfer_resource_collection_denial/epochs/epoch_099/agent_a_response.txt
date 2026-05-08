def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    blocked = {(p[0], p[1]) for p in obstacles}

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    safe = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            safe.append((dx, dy, nx, ny))
    if not safe:
        return [0, 0]

    if not resources:
        best = None
        for dx, dy, nx, ny in safe:
            d = man(nx, ny, ox, oy)
            if best is None or d < best[0] or (d == best[0] and (dx, dy) < (best[1], best[2])):
                best = (d, dx, dy)
        return [best[1], best[2]]

    # density: prefer clusters of resources to reduce chance of missing due to denier behavior
    dens = {}
    for rx, ry in resources:
        c = 0
        for ax, ay in resources:
            if man(rx, ry, ax, ay) <= 2:
                c += 1
        dens[(rx, ry)] = c

    # choose target maximizing lead and density
    best_t = None  # (score, rx, ry)
    for rx, ry in resources:
        myt = man(sx, sy, rx, ry)
        ot = man(ox, oy, rx, ry)
        lead = ot - myt  # positive means we arrive earlier
        # Encourage finishing closer to current position, but not at cost of losing lead.
        score = lead * 4 + dens[(rx, ry)] * 2 - myt * 0.2
        # deterministic tie-break: higher score, then smaller myt, then lexicographic
        cand = (score, -man(sx, sy, rx, ry), rx, ry)
        if best_t is None or cand > best_t:
            best_t = cand
    _, _, tx, ty = best_t

    # pick move that maximizes resulting lead; deterministic tie-breaks
    best = None  # (lead2, -dist2, dx, dy)
    for dx, dy, nx, ny in safe:
        myd = man(nx, ny, tx, ty)
        othd = man(ox, oy, tx, ty)
        # lead after move: higher is better
        lead2 = othd - myd
        cand = (lead2, -myd, dx, dy)
        if best is None or cand > best:
            best = cand
    return [best[2], best[3]]