def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    occ = {(p[0], p[1]) for p in obstacles}

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources:
        return [0, 0]

    best = None
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if (nx, ny) in occ or nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue

        # Base: maximize how much closer we would be to some resource than the opponent.
        score = 0
        local_best_gap = -10**18
        min_my = 10**9

        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            gap = opd - myd
            if gap > local_best_gap:
                local_best_gap = gap
            if myd < min_my:
                min_my = myd

        # Contest priority + progress priority
        score += local_best_gap * 2200
        score += -min_my * 25

        # Obstacle/edge avoidance: penalize moves adjacent to obstacles
        adj_pen = 0
        for ax, ay in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
            tx, ty = nx + ax, ny + ay
            if 0 <= tx < w and 0 <= ty < h and (tx, ty) in occ:
                adj_pen -= 40
        score += adj_pen

        # Small bias to move generally toward the center (to avoid corner stagnation)
        cx, cy = (w - 1) // 2, (h - 1) // 2
        score += -cheb(nx, ny, cx, cy) * 2

        if score > best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]