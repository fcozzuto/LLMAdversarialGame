def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    obs = observation.get("obstacles", []) or []
    obstacles = set(map(tuple, obs))
    resources = observation.get("resources", []) or []
    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def blocked(x, y):
        return (x, y) in obstacles

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    # If no explicit resources, fall back to chasing opponent
    if not resources:
        best = None
        bestd = 10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or blocked(nx, ny):
                continue
            d = man(nx, ny, ox, oy)
            if d < bestd or (d == bestd and (dx, dy) < best):
                bestd, best = d, (dx, dy)
        return list(best if best is not None else [0, 0])

    resources = [tuple(r) for r in resources]
    best = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue

        # Score: prefer move that reduces my distance more than opponent's to the nearest resource.
        my_best = 10**9
        opp_best = 10**9
        for rx, ry in resources:
            d1 = man(nx, ny, rx, ry)
            d2 = man(ox, oy, rx, ry)
            if d1 < my_best:
                my_best = d1
            if d2 < opp_best:
                opp_best = d2
        score = (opp_best - my_best)

        # Tie-break deterministically toward closer to opponent (more aggressive)
        if score > best_score or (score == best_score and man(nx, ny, ox, oy) < man(sx + best[0], sy + best[1], ox, oy)):
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]