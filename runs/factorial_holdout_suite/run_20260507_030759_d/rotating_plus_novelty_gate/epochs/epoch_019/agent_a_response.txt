def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    legal = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                legal.append((dx, dy))
    if not legal:
        return [0, 0]

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def best_resource_dist(px, py):
        if not resources:
            return 10**9, None
        dmin = 10**9
        pick = resources[0]
        for rx, ry in resources:
            d = man(px, py, rx, ry)
            if d < dmin:
                dmin = d
                pick = (rx, ry)
        return dmin, pick

    if not resources:
        # Retreat: maximize distance from opponent, tie-break by staying centered-ish.
        best = None
        bestv = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            v = (man(nx, ny, ox, oy), -abs(nx - (w - 1) / 2) - abs(ny - (h - 1) / 2), -nx, -ny)
            if bestv is None or v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Main: for each move, compare our nearest resource distance vs opponent's nearest,
    # with a small bonus for moving closer to the overall nearest resource.
    best = (0, 0)
    bestv = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        d_self, _ = best_resource_dist(nx, ny)
        d_opp, _ = best_resource_dist(ox, oy)

        # If opponent is closer to some resource than us, prefer moves that widen the gap.
        # Also, slightly prioritize progress (smaller d_self).
        gap = d_opp - d_self
        v = (gap, -d_self, -man(nx, ny, ox, oy), -nx, -ny)
        if bestv is None or v > bestv:
            bestv = v
            best = (dx, dy)

    return [best[0], best[1]]