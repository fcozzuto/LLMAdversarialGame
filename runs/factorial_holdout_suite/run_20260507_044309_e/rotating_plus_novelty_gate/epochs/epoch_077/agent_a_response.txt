def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    resources = observation.get("resources", []) or []
    if not (0 <= sx < w and 0 <= sy < h):
        return [0, 0]

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    immediate = set(tuple(r) for r in resources)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny) and (nx, ny) in immediate:
            return [dx, dy]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        best = None
        bestd = 10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            if d < bestd:
                bestd = d
                best = (dx, dy)
        return [best[0], best[1]] if best is not None else [0, 0]

    best_score = -10**18
    best_t = None
    for i, (rx, ry) in enumerate(resources):
        myd = cheb(sx, sy, rx, ry)
        opd = cheb(ox, oy, rx, ry)
        # Prefer resources I can reach at least as fast; otherwise choose the one that hurts opponent the most.
        score = (opd - myd) * 100
        if myd <= opd:
            score += 10000 - i  # deterministic tie-break favor earlier-listed resources
        # Small preference for reducing distance overall.
        score -= myd
        # Slight bias toward resources "above" opponent in y (helps intercept in many layouts).
        if (sy - ry) * (oy - ry) < 0:
            score += 5
        if score > best_score:
            best_score = score
            best_t = (rx, ry)

    tx, ty = best_t
    best = None
    bestd = 10**9
    best_block = 10**9
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            continue
        d = cheb(nx, ny, tx, ty)
        # Secondary metric: stay away from obstacles by penalizing proximity in a tiny way (local only).
        block_pen = 0
        for bx, by in obstacles:
            dd = cheb(nx, ny, bx, by)
            if dd <= 1:
                block_pen += 3 - dd
        if d < bestd or (d == bestd and block_pen < best_block):
            bestd = d
            best_block = block_pen
            best = (dx, dy)

    return [best[0], best[1]] if best is not None else [0, 0]