def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if resources:
        best = None
        bestv = None
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            oppd = cheb(ox, oy, rx, ry)
            v = (oppd - myd) * 1000 - myd
            if bestv is None or v > bestv or (v == bestv and (rx, ry) < best):
                bestv = v
                best = (rx, ry)
        tx, ty = best
    else:
        # No visible resources: move to a corner that maximizes distance from opponent
        corners = [(0,0),(0,h-1),(w-1,0),(w-1,h-1)]
        best = None
        bestv = None
        for cx, cy in corners:
            v = cheb(ox, oy, cx, cy) - cheb(sx, sy, cx, cy)
            if bestv is None or v > bestv or (v == bestv and (cx, cy) < best):
                bestv = v
                best = (cx, cy)
        tx, ty = best

    best_move = (0, 0)
    best_score = None
    # Prefer moves that reduce our distance to target and increase opponent's distance.
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        oppd = cheb(ox, oy, tx, ty)
        # Tie-break deterministically with position preference
        score = (-myd) + (oppd - myd) * 0.001 + (-abs((nx - tx)) - abs((ny - ty))) * 1e-6
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    # If all moves invalid, stay.
    return [int(best_move[0]), int(best_move[1])]