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

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles

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

    def md(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def step_toward(tx, ty):
        best = (10**9, None)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            d = md(nx, ny, tx, ty)
            # tie-break deterministically by direction order already in moves
            if d < best[0]:
                best = (d, (dx, dy))
        return best[1] if best[1] is not None else (0, 0)

    # Select a target resource: prioritize where we are closer than opponent; then maximize lead.
    best_target = None
    best_key = None  # lower is better
    for (rx, ry) in resources:
        ds = md(sx, sy, rx, ry)
        do = md(ox, oy, rx, ry)
        # Key: prefer we can reach earlier; reward larger negative (opponent farther)
        reach_gap = do - ds
        key = (-reach_gap, ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_target = (rx, ry)

    if best_target is not None:
        tx, ty = best_target
        return list(step_toward(tx, ty))

    # If no resources known, drift toward center while avoiding obstacles.
    cx, cy = (w - 1) // 2, (h - 1) // 2
    return list(step_toward(cx, cy))