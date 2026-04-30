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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not free(sx, sy):
        for dx, dy in moves:
            if free(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if free(x, y):
                resources.append((x, y))

    def dist(a, b, c, d):
        ax = a - c
        if ax < 0:
            ax = -ax
        ay = b - d
        if ay < 0:
            ay = -ay
        return ax + ay

    if not resources:
        # Deterministically head toward center while keeping distance from opponent
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            v = -dist(nx, ny, cx, cy) + 0.5 * dist(nx, ny, ox, oy)
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv, best = v, (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    # Score each move by best resource it could pursue next (greedy), while discouraging closing to opponent
    best = None
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue

        # Prefer resources that are closer now; break ties by (1) relative advantage over opponent, then (2) resource order
        mv_best = -10**18
        for i, (rx, ry) in enumerate(resources):
            d_self = dist(nx, ny, rx, ry)
            d_opp = dist(ox, oy, rx, ry)
            # If we are closer (or less behind), boost; otherwise penalize.
            rel = d_opp - d_self
            v = -d_self + 0.35 * rel + 0.12 * dist(nx, ny, ox, oy) - 1e-6 * i
            if v > mv_best:
                mv_best = v
        vfinal = mv_best
        if vfinal > bestv or (vfinal == bestv and (dx, dy) < best):
            bestv, best = vfinal, (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]