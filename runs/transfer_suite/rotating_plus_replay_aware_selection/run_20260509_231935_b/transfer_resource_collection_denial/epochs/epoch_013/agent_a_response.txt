def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist8(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1),
            (1, 1), (1, -1), (-1, 1), (-1, -1))

    if not resources:
        cx, cy = w // 2, h // 2
        best = (10**9, 0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                nx, ny = sx, sy
            d = dist8(nx, ny, cx, cy)
            cand = (d, dx, dy)
            if cand < best:
                best = cand
        return [best[1], best[2]]

    k = 0.9  # emphasize racing opponent
    best_score = -10**18
    best_move = (0, 0)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy

        # Choose best "resource race" from this next position.
        local_best = -10**18
        for rx, ry in resources:
            md = dist8(nx, ny, rx, ry)
            od = dist8(ox, oy, rx, ry)
            # Higher is better: win the race, then prefer nearer own distance.
            score = (od - md) * k - md * 0.05
            if score > local_best:
                local_best = score

        # Small preference for moving closer to any resource to reduce dithering.
        # (deterministic tie-break: lexicographic by move order)
        min_md_next = 10**9
        for rx, ry in resources:
            d = dist8(nx, ny, rx, ry)
            if d < min_md_next:
                min_md_next = d
        score_total = local_best - min_md_next * 0.005

        if score_total > best_score:
            best_score = score_total
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]