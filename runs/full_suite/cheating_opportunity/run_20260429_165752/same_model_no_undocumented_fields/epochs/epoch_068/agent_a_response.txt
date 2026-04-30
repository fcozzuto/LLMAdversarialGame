def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if free(x, y):
                resources.append((x, y))

    def cd(x1, y1, x2, y2):
        a = x1 - x2
        if a < 0: a = -a
        b = y1 - y2
        if b < 0: b = -b
        return a if a > b else b

    if not free(sx, sy):
        moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        for dx, dy in moves:
            if free(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        # Deterministic fallback: move to increase distance from opponent (safer) if possible.
        best = (-10**9, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            sc = cd(nx, ny, ox, oy)
            if sc > best[0]:
                best = (sc, dx, dy)
        return [best[1], best[2]]

    # Choose a target resource we are relatively more competitive for.
    best_res = resources[0]
    best_key = None
    for rx, ry in resources:
        myd = cd(sx, sy, rx, ry)
        opd = cd(ox, oy, rx, ry)
        # Key: smaller is better: myd, but penalize if opponent is closer.
        key = (myd, myd - opd)
        if best_key is None or key < best_key or (key == best_key and (rx, ry) < best_res):
            best_key = key
            best_res = (rx, ry)

    rx, ry = best_res
    best_sc, best_dx, best_dy = -10**18, 0, 0
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        myd2 = cd(nx, ny, rx, ry)
        # Prefer approaching target; slightly prefer being farther from opponent.
        # Also avoid stepping into positions from which opponent is much closer to the target.
        opd2 = cd(ox, oy, rx, ry)
        oppd = cd(nx, ny, ox, oy)
        sc = -myd2 * 100 + oppd - (myd2 - opd2) * 5
        # Deterministic tie-break by move ordering through strict comparisons.
        if sc > best_sc:
            best_sc, best_dx, best_dy = sc, dx, dy

    return [int(best_dx), int(best_dy)]