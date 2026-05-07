def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []

    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx >= dy else dy

    dirs = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]
    if not resources:
        return [0, 0]

    # Deterministic "race" scoring with mild center bias to reduce oscillation.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def best_value_from(px, py):
        best = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            ds = cheb(px, py, rx, ry)
            do = cheb(ox, oy, rx, ry)
            # If we are faster, value increases strongly; if slower, discourage.
            race = (do - ds)
            center = 0.02 * (-(abs(rx - cx) + abs(ry - cy)))
            # Tie-break: prefer smaller self distance once race is similar.
            v = (race * 1000) + center - ds * 0.001
            if best is None or v > best[0]:
                best = (v, ds, do)
        return best

    # Strategic change: do one-step lookahead and pick move maximizing the best target value,
    # but if all moves look bad (no race advantage), pull toward the closest resource.
    scored = []
    for dx, dy, nx, ny in legal:
        val, ds, do = best_value_from(nx, ny)
        scored.append((val, -ds, do, dx, dy))

    scored.sort(reverse=True)
    best = scored[0]
    best_val = best[0]

    # If we can't beat opponent on any reasonable next move, switch to closest-to-ahead resource.
    # (Prevents slow losing races where opportunistic target swaps caused regression.)
    if best_val < -5:
        # Choose move that minimizes (self_dist - opponent_dist) toward nearest resource while staying safe.
        def fallback_value(px, py):
            bestf = None
            for r in resources:
                rx, ry = int(r[0]), int(r[1])
                ds = cheb(px, py, rx, ry)
                do = cheb(ox, oy, rx, ry)
                v = (ds - do) * 1000 + ds * 1.0  # smaller is better
                if bestf is None or v < bestf:
                    bestf = v
            return bestf

        best_move = None
        bestfv = None
        for dx, dy, nx, ny in legal:
            fv = fallback_value(nx, ny)
            if bestfv is None or fv < bestfv:
                bestfv = fv
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    return [int(best[3]), int(best[4])]