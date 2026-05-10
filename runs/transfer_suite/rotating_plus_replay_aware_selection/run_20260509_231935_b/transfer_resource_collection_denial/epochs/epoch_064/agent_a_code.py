def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    if not resources:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def step_toward(tx, ty):
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            return [dx, dy]
        # try axis-aligned fallbacks deterministically
        candidates = [[dx, 0], [0, dy], [0, 0]]
        for m in candidates:
            nx, ny = sx + m[0], sy + m[1]
            if inb(nx, ny) and (nx, ny) not in obs:
                return m
        return [0, 0]

    best = None
    best_key = None
    for p in resources:
        if not p or len(p) < 2:
            continue
        rx, ry = p[0], p[1]
        if (rx, ry) in obs:
            continue

        d_self = cheb(sx, sy, rx, ry)
        d_opp = cheb(ox, oy, rx, ry)
        # Prefer resources we can reach no later than opponent; otherwise deny by maximizing distance advantage.
        reachable = 1 if d_self <= d_opp else 0
        dist_adv = d_opp - d_self  # larger is better
        # Also slightly prefer closer absolute targets to reduce time-to-pickup.
        key = (reachable, dist_adv, -d_self, -((rx + ry) % 7))
        if best is None or key > best_key:
            best = (rx, ry)
            best_key = key

    if best is None:
        return [0, 0]
    return step_toward(best[0], best[1])