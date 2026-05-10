def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    self_t = set(map(tuple, observation.get("self_territory", [])))
    opp_t = set(map(tuple, observation.get("opponent_territory", [])))
    unclaimed = set(map(tuple, observation.get("unclaimed_cells", [])))
    obstacles = set(map(tuple, observation.get("obstacles", [])))
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def man(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]
    d_center = (w - 1) / 2.0, (h - 1) / 2.0
    ccx, ccy = d_center

    # If opponent is behind, be slightly more territorial; if ahead, be more aggressive.
    self_cnt = observation.get("self_territory_count", len(self_t))
    opp_cnt = observation.get("opponent_territory_count", len(opp_t))
    aggressive = 2.1 if opp_cnt >= self_cnt else 1.15

    best_move = [0, 0]
    best_v = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue

        target = (nx, ny)
        v = 0.0

        # Strongly prefer capturing opponent territory (flipping on entry).
        if target in opp_t:
            v += 300.0 * aggressive
            v -= 1.2 * man(nx, ny, ox, oy)
            # If stepping closer to opponent reduces their ability to escape, add a bit.
            v += 10.0 / (1 + man(nx, ny, sx, sy))
        else:
            # Prefer stepping into unclaimed (claiming) or our own territory (stability).
            if target in unclaimed:
                v += 55.0
            elif target in self_t:
                v += 18.0
            else:
                v += 8.0

            # Bias toward the opponent: territory sweeper types often spread; aim to intersect.
            v += 8.0 * aggressive / (1 + man(nx, ny, ox, oy))

            # Avoid drifting into corners/edges too much unless it helps approach opponent.
            v -= 0.8 * (abs(nx - ccx) + abs(ny - ccy)) / max(w + h, 1)

            # If unclaimed exists, head toward the nearest one; else keep toward opponent.
            if unclaimed:
                # Evaluate a small deterministic subset to keep runtime low.
                # Use top-4 closest-by-Manhattan from current position.
                scored = []
                for ux, uy in unclaimed:
                    scored.append((man(nx, ny, ux, uy), ux, uy))
                scored.sort(key=lambda t: t[0])
                nearest_d = scored[0][0] if scored else man(nx, ny, ox, oy)
                v += 30.0 / (1 + nearest_d)
            else:
                v += 10.0 / (1 + man(nx, ny, ox, oy))

            # Discourage oscillation by preferring moves that change Manhattan distance to opponent.
            v += -0.5 * (man(nx, ny, ox, oy) - man(sx, sy, ox, oy))

        # Prefer moves not blocked by adjacency congestion (deterministic: count obstacles around target).
        obs_nei = 0
        for adx, ady in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]:
            tx, ty = nx + adx, ny + ady
            if inb(tx, ty) and (tx, ty) in obstacles:
                obs_nei += 1
        v -= 6.0 * obs_nei

        if v > best_v:
            best_v = v
            best_move = [dx, dy]

    return best_move