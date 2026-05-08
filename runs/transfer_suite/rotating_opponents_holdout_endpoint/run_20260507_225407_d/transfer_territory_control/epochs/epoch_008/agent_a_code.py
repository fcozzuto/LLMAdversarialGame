def choose_move(observation):
    sx, sy = observation["self_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    ox, oy = observation.get("opponent_position", (sx, sy))
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_cells = set(tuple(p) for p in (observation.get("self_territory") or []))
    opp_cells = set(tuple(p) for p in (observation.get("opponent_territory") or []))
    unclaimed = set(tuple(p) for p in (observation.get("unclaimed_cells") or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    dirs = [(0, 1), (1, 0), (0, 0), (0, -1), (-1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    target = None
    if unclaimed:
        bestd = 10**9
        for cx, cy in unclaimed:
            if (cx, cy) in obstacles:
                continue
            d = abs(cx - ox) + abs(cy - oy)
            if d < bestd or (d == bestd and (cx < target[0] or (cx == target[0] and cy < target[1]))):
                bestd = d
                target = (cx, cy)
    if target is None:
        target = ((w - 1) // 2, (h - 1) // 2)

    best = (-10**18, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        cell = (nx, ny)
        score = 0
        if cell in opp_cells:
            score += 1000000
        if cell in unclaimed:
            score += 2000
        if cell in self_cells:
            score += 5
        d = abs(nx - target[0]) + abs(ny - target[1])
        score -= d * 3
        d_op = abs(nx - ox) + abs(ny - oy)
        score -= d_op
        if score > best[0] or (score == best[0] and (dx, dy) < (best[1], best[2])):
            best = (score, dx, dy)

    dx, dy = best[1], best[2]
    return [int(dx), int(dy)]