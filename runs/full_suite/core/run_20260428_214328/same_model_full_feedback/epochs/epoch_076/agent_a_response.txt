def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def man(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx + dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = None
    best_val = -10**18

    if not resources:
        # Deterministic fallback: move to reduce distance to center
        cx, cy = (w - 1) // 2, (h - 1) // 2
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                v = -man(nx, ny, cx, cy)
                if v > best_val:
                    best_val, best = v, (dx, dy)
        if best is None:
            return [0, 0]
        return [int(best[0]), int(best[1])]

    # Strategy: prefer moves that create the biggest advantage on at least one resource,
    # while also keeping overall distance small.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue

        my_best_gap = -10**18
        my_best_dist = 10**18
        for rx, ry in resources:
            myd = man(nx, ny, rx, ry)
            opd = man(ox, oy, rx, ry)
            gap = opd - myd  # positive means we are closer than opponent to that resource
            if gap > my_best_gap:
                my_best_gap = gap
            if myd < my_best_dist:
                my_best_dist = myd

        # Extra tie-break: if we can potentially secure something soon (small myd when gap>0), prioritize.
        # Penalize moves that move away from any resource.
        v = (my_best_gap * 100) - my_best_dist
        if v > best_val:
            best_val, best = v, (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]