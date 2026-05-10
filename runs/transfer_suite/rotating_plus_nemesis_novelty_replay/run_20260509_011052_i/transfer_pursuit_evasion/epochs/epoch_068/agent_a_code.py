def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    self_role = (observation.get("self_role") or "").lower()
    pursuer = ("pursuer" in self_role) and ("evader" not in self_role)

    dirs = [(-1, -1), (0, -1), (1, -1),
            (-1, 0),  (0, 0),  (1, 0),
            (-1, 1),  (0, 1),  (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def mobility(x, y):
        m = 0
        for dx, dy in dirs:
            if inb(x + dx, y + dy):
                m += 1
        return m

    best = None
    if pursuer:
        best_val = -10**18
    else:
        best_val = 10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue

        d = cheb(nx, ny, ox, oy)
        # capture radius 0: exact match is overwhelming
        if nx == ox and ny == oy:
            val = 10**12 if pursuer else -10**12
        else:
            # pursuer wants smaller distance; evader wants larger distance
            dist_term = -d if pursuer else d

            # discourage getting stuck near obstacles/edges
            mob = mobility(nx, ny)
            mob_term = mob if pursuer else -mob

            # prefer moves that increase/decrease Chebyshev distance consistently
            prev_d = cheb(sx, sy, ox, oy)
            delta = d - prev_d
            trend_term = -delta if pursuer else delta  # negative delta helps pursuer

            # weight to favor direct pressure, then safety
            val = (3.0 * dist_term) + (0.7 * mob_term) + (0.4 * trend_term)

        if pursuer:
            if val > best_val:
                best_val = val
                best = (dx, dy)
            elif val == best_val and best is not None:
                # deterministic tie-break: lexicographic preference
                if (dx, dy) < best:
                    best = (dx, dy)
        else:
            if val < best_val:
                best_val = val
                best = (dx, dy)
            elif val == best_val and best is not None:
                if (dx, dy) < best:
                    best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]