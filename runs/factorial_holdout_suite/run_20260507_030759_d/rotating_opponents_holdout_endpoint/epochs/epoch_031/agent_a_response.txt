def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and inb(x, y):
                res.append((x, y))

    if not res:
        return [0, 0]

    allowed = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if inb(sx + dx, sy + dy)]
    if not allowed:
        return [0, 0]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0:
            dx = -dx
        dy = b - d
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    # Precompute resource values from current state
    # Higher is better: (opp_take_risk) -> small self_dist and large opp_dist
    def cell_value(x, y):
        best = None
        for rx, ry in res:
            sd = cheb(sx, sy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Better if opponent is farther, and if we're closer.
            # Also slightly prefer closer resources to reduce path length.
            val = (od - sd, -sd)
            if best is None or val > best:
                best = val
        # If resources exist, best can't be None
        return best[0] * 2 - (-best[1])

    best_move = (0, 0)
    best_score = None
    for dx, dy in allowed:
        nx, ny = sx + dx, sy + dy
        # Evaluate by "best resource we could claim from here"
        # Primary: maximize (opp_dist - self_dist), Secondary: minimize self_dist, Tertiary: prefer not moving away
        best = None
        for rx, ry in res:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Winning pressure: can we get there earlier/equally?
            pressure = od - sd
            # If sd large, value decreases. If pressure same, prefer smaller sd.
            val = (pressure, -sd, -cheb(sx, sy, rx, ry))
            if best is None or val > best:
                best = val
        score = best[0] * 3 + best[1]
        # Small deterministic tie-break to reduce dithering: prefer diagonal/forward toward the current best resource
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]