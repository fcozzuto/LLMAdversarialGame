def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    valid = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if (dx, dy) == (0, 0):
                valid.append((0, 0))
                continue
            if inb(nx, ny) and (nx, ny) not in obs:
                valid.append((dx, dy))
    if not valid:
        return [0, 0]

    def cheb(a, b, c, d):
        dx = abs(a - c)
        dy = abs(b - d)
        return dx if dx > dy else dy

    if not resources:
        corners = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]
        far = None
        bestd = -1
        for cx, cy in corners:
            d = cheb(ox, oy, cx, cy)
            if d > bestd:
                bestd = d
                far = (cx, cy)
        tx, ty = far
        best = min(valid, key=lambda m: cheb(sx + m[0], sy + m[1], tx, ty))
        return [best[0], best[1]]

    # Pick a target resource based on whether we are closer than the opponent (ignores obstacles for speed).
    best_res = None
    best_key = None
    for rx, ry in resources:
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        advantage = od - sd  # larger => we are closer or opponent farther
        key = (-advantage, sd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_res = (rx, ry)

    rx, ry = best_res

    # If adjacent (including diagonal), deterministically step onto it.
    for dx, dy in valid:
        if sx + dx == rx and sy + dy == ry:
            return [dx, dy]

    # Otherwise, choose move that best reduces distance to chosen target, with a slight anti-denial bias:
    # also avoid making us relatively closer to resources where opponent is already closer.
    best_move = None
    best_move_key = None
    for dx, dy in valid:
        nx, ny = sx + dx, sy + dy
        sd = cheb(nx, ny, rx, ry)
        # compute minimal opponent-self advantage over all resources after move
        worst = None
        for r2x, r2y in resources:
            s2d = cheb(nx, ny, r2x, r2y)
            o2d = cheb(ox, oy, r2x, r2y)
            adv2 = o2d - s2d
            if worst is None or adv2 < worst:
                worst = adv2
        # Prefer smaller distance to target; then prefer not to give opponent too much reach (maximize worst advantage)
        key = (sd, -worst, r2x if False else 0, dx, dy)
        if best_move_key is None or key < best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]