def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    obstacles = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y):
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if inb(x, y) and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Choose a resource where we arrive no later than opponent, with tie-break bias away from opponent.
    best_r = resources[0]
    best_score = -10**18
    for rx, ry in resources:
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        tie_bias = abs(rx - ox) - abs(ry - oy)
        score = (opd - myd) * 100 + tie_bias
        if score > best_score:
            best_score = score
            best_r = (rx, ry)
        elif score == best_score:
            # deterministic secondary: prefer smaller myd, then lexicographic
            if (myd, rx, ry) < (cheb(sx, sy, best_r[0], best_r[1]), best_r[0], best_r[1]):
                best_r = (rx, ry)

    rx, ry = best_r
    dx = 0 if rx == sx else (1 if rx > sx else -1)
    dy = 0 if ry == sy else (1 if ry > sy else -1)

    # Candidate moves (prefer toward target, then other directions).
    candidates = [
        (dx, dy),
        (dx, 0),
        (0, dy),
        (dx, -dy),
        (-dx, dy),
        (-dx, 0),
        (0, -dy),
        (-dx, -dy),
        (0, 0),
    ]
    seen = set()
    for mx, my in candidates:
        if (mx, my) in seen:
            continue
        seen.add((mx, my))
        nx, ny = sx + mx, sy + my
        if inb(nx, ny) and (nx, ny) not in obstacles:
            # ensure the choice still moves closer to chosen target under Chebyshev
            if cheb(nx, ny, rx, ry) <= cheb(sx, sy, rx, ry) or (mx == 0 and my == 0):
                return [int(mx), int(my)]

    # Fallback: any valid step (still deterministic order), else stay.
    for mx in (-1, 0, 1):
        for my in (-1, 0, 1):
            nx, ny = sx + mx, sy + my
            if inb(nx, ny) and (nx, ny) not in obstacles:
                return [int(mx), int(my)]
    return [0, 0]