def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    def toset(v):
        s = set()
        for p in (v or []):
            if isinstance(p, (list, tuple)) and len(p) >= 2:
                s.add((int(p[0]), int(p[1])))
        return s

    obstacles = toset(observation.get("obstacles"))
    unclaimed = toset(observation.get("unclaimed_cells"))
    resources = toset(observation.get("resources"))
    selfT = toset(observation.get("self_territory"))
    oppT = toset(observation.get("opponent_territory"))

    if not unclaimed:
        unclaimed = set(resources)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h

    # Prefer paths that (1) capture opponent territory (on entry), (2) secure unclaimed,
    # (3) bias toward the board center while not drifting away from potential frontiers.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    def dist(a, b): 
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    target_point = None
    if unclaimed:
        # deterministic closest-to-self unclaimed, but also slightly attracted to opponent proximity
        best = None
        for c in sorted(unclaimed):
            d = abs(c[0] - sx) + abs(c[1] - sy)
            da = abs(c[0] - ox) + abs(c[1] - oy)
            sc = d + 0.15 * da
            if best is None or sc < best[0]:
                best = (sc, c)
        target_point = best[1]
    elif resources:
        target_point = min(sorted(resources), key=lambda c: (dist(c, (sx, sy)), c[0], c[1]))

    best_move = [0, 0]
    best_sc = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        sc = 0
        if (nx, ny) in oppT:
            sc += 12  # flipping-on-entry is strong
        elif (nx, ny) in unclaimed:
            sc += 5
        elif (nx, ny) in selfT:
            sc += 2

        # Center pressure and frontier seeking
        sc += -0.6 * (abs(nx - cx) + abs(ny - cy))
        if target_point is not None:
            sc += -1.0 * (abs(nx - target_point[0]) + abs(ny - target_point[1]))
        # Avoid stepping away from opponent when we can potentially contest their area
        sc += -0.08 * (abs(nx - ox) + abs(ny - oy))

        if sc > best_sc or (sc == best_sc and (dx, dy) < (best_move[0], best_move[1])):
            best_sc = sc
            best_move = [dx if inb(sx+dx, sy+dy) and (sx+dx, sy+dy) not in obstacles else 0,
                          dy if inb(sx+dx, sy+dy) and (sx+dx, sy+dy) not in obstacles else 0]

    return best_move