def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (w - 1, h - 1))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = observation.get("obstacles", []) or []
    obst = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            obst.add((int(p[0]), int(p[1])))

    resources = observation.get("resources", []) or []
    res = []
    for p in resources:
        if p is not None and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                res.append((x, y))

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0: ax = -ax
        by = y1 - y2
        if by < 0: by = -by
        return ax if ax > by else by

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny) and (nx, ny) not in obst and (nx, ny) != (ox, oy):
            legal.append((dx, dy, nx, ny))
    if not legal:
        return [0, 0]

    if not res:
        # Deterministic escape: keep moving to increase distance from opponent when blocked
        best = None
        bestv = None
        for dx, dy, nx, ny in legal:
            v = cheb(nx, ny, ox, oy)
            if bestv is None or v > bestv or (v == bestv and (dx, dy) < best):
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    # Pick a target that is relatively closer to us than to opponent
    best_r = None
    best_k = None
    for rx, ry in res:
        dself = cheb(sx, sy, rx, ry)
        do = cheb(ox, oy, rx, ry)
        # Prefer resources we are closer to; break ties by smaller dself then coordinates
        k = (dself - do, dself, rx, ry)
        if best_k is None or k < best_k:
            best_k = k
            best_r = (rx, ry)

    tr, ty = best_r

    # One-step greedy toward target, but penalize moves that make us much worse vs opponent
    best = None
    best_score = None
    for dx, dy, nx, ny in legal:
        d_to_target = cheb(nx, ny, tr, ty)
        my_near = min(cheb(nx, ny, rx, ry) for rx, ry in res) if res else 0
        opp_near = min(cheb(ox, oy, rx, ry) for rx, ry in res) if res else 0
        # Strongly prefer decreasing distance to target; also keep advantage over opponent
        score = (-d_to_target) + 0.35 * (opp_near - my_near) + 0.01 * cheb(nx, ny, ox, oy)
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    return [int(best[0]), int(best[1])]