def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    dirs = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def clamp_in(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    # Pick a resource we can reach first (Chebyshev distance), with strong advantage vs opponent.
    if resources:
        best = None
        bestv = None
        for rx, ry in resources:
            myd = cheb(sx, sy, rx, ry)
            oppd = cheb(ox, oy, rx, ry)
            # Prioritize larger (oppd - myd), then smaller myd, then stable tie-break by position.
            v = (oppd - myd) * 1000 - myd
            if bestv is None or v > bestv or (v == bestv and (rx, ry) < best):
                bestv = v
                best = (rx, ry)
        tx, ty = best
    else:
        # No visible resources: head to corner farthest from opponent.
        corners = [(0,0),(0,h-1),(w-1,0),(w-1,h-1)]
        best = None
        bestv = None
        for cx, cy in corners:
            v = -cheb(ox, oy, cx, cy)
            if bestv is None or v > bestv or (v == bestv and (cx, cy) < best):
                bestv = v
                best = (cx, cy)
        tx, ty = best

    # Choose best neighbor toward target, avoiding obstacles.
    bestmove = (0, 0)
    bestscore = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not clamp_in(nx, ny):
            continue
        myd = cheb(nx, ny, tx, ty)
        oppd = cheb(ox, oy, tx, ty)
        # Higher is better: maximize advantage and reduce our distance.
        score = (oppd - myd) * 1000 - myd
        # Small tie-break: prefer moves that also reduce distance to target lexicographically.
        if bestscore is None or score > bestscore or (score == bestscore and (dx, dy) < bestmove):
            bestscore = score
            bestmove = (dx, dy)

    return [int(bestmove[0]), int(bestmove[1])]