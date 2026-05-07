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

    # Deterministic ordering for tie-breaks
    res = sorted((tuple(r) for r in resources), key=lambda p: (p[0], p[1]))
    oppd = man

    if not res:
        # No visible resources: move to maximize distance and center bias
        best = None
        bestv = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            v = (oppd(nx, ny, ox, oy),
                 -abs(nx - (w - 1) / 2) - abs(ny - (h - 1) / 2),
                 -nx, -ny)
            if bestv is None or v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Prefer resources we are closer to than opponent, otherwise reduce the gap.
    best = None
    bestv = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        best_adv = -10**9
        best_self = 10**9
        for rx, ry in res:
            sd = man(nx, ny, rx, ry)
            od = man(ox, oy, rx, ry)
            adv = od - sd  # positive means we are closer
            # If equal distances, slight preference for picking sooner (lower sd).
            v = (adv, -sd, -rx, -ry)
            if v > (best_adv, -best_self, -rx, -ry):
                best_adv = adv
                best_self = sd
        # Secondary: also slightly prefer moving toward the best resource direction (encoded by best_self)
        v2 = (best_adv, -best_self, -nx, -ny)
        if bestv is None or v2 > bestv:
            bestv = v2
            best = (dx, dy)
    return [best[0], best[1]]