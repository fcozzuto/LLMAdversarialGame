def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if not (0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cd(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]

    if not resources:
        tx, ty = (0, h - 1) if (ox + oy) % 2 else (w - 1, 0)
        best = None
        bestk = None
        for dx, dy, nx, ny in valid:
            k = (cd(nx, ny, tx, ty), dx, dy)
            if bestk is None or k < bestk:
                bestk = k
                best = (dx, dy)
        return [best[0], best[1]]

    # Denier-aware: move to the resource we can reach first (relative to opponent), else block by moving toward the resource the opponent is closest to.
    bestk = None
    best_move = (0, 0)
    for dx, dy, nx, ny in valid:
        our_best = None  # (score, self_dist, res_x, res_y)
        for rx, ry in resources:
            d_our = cd(nx, ny, rx, ry)
            d_opp = cd(ox, oy, rx, ry)
            # Higher is better for our_best.score
            score = (d_opp - d_our)
            # Captures dominate
            if d_our == 0:
                score = 10**6
            item = (score, -d_our, rx, ry)
            if our_best is None or item > our_best:
                our_best = item
        # Lexicographic tie-break on resulting position to stay deterministic
        score, ndour, rx, ry = our_best
        k = (-score, nx, ny, dx, dy, rx, ry)
        if bestk is None or k < bestk:
            bestk = k
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]