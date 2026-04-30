def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    blocked = set()
    for p in (observation.get("obstacles") or []):
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    resources = []
    for r in (observation.get("resources") or []):
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y):
                resources.append((x, y))

    dirs = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    legal = [(dx, dy) for dx, dy in dirs if inb(sx + dx, sy + dy)]
    if not legal:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # If no resources visible, head to center while avoiding obstacles.
    if not resources:
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best = None
        bestv = -10**18
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            dist = cheb(nx, ny, cx, cy)
            score = -dist
            if score > bestv:
                bestv = score
                best = (dx, dy)
        return [int(best[0]), int(best[1])] if best else [0, 0]

    # Main idea: maximize (my advantage) toward contested resources,
    # with small tie-break for closer-than-opponent movement.
    best = None
    bestv = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        my_best = -10**18
        for rx, ry in resources:
            md = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Positive when I'm at least as close as opponent; strong bias for winning a resource.
            adv = (od - md)
            # Prefer removing my local obstacle risk by encouraging moves that reduce my distance.
            local = -md
            cand = adv * 10 + local
            if cand > my_best:
                my_best = cand
        # Slight preference to reduce own distance to the nearest resource when generally tied.
        v = my_best
        if v > bestv:
            bestv = v
            best = (dx, dy)
        elif v == bestv and best is not None:
            # Deterministic tie-break: prefer staying, then lexicographic by dx,dy order in dirs.
            if (dx, dy) == (0, 0):
                best = (dx, dy)
    return [int(best[0]), int(best[1])] if best else [0, 0]