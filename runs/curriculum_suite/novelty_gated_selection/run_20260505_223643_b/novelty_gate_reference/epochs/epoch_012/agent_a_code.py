def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set((int(p[0]), int(p[1])) for p in obstacles_list)

    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best = [0, 0, -10**18]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    # Pick target deterministically: nearest resource; tie-break by lexicographic.
    target = None
    if resources:
        best_key = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            d = cheb(sx, sy, rx, ry)
            key = (d, rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                target = (rx, ry)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Avoid staying put if movement is possible.
        move_bias = 1 if (dx != 0 or dy != 0) else 0

        # Resource progress / denial.
        res_score = 0
        if target:
            rx, ry = target
            myd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Prefer closing distance if we can beat opponent to it.
            res_score = (od - myd) * 10 - myd
            if (ox, oy) == (rx, ry):
                res_score -= 50

        # Opponent pressure: when resource race is unclear, move away slightly.
        opp_dist = cheb(nx, ny, ox, oy)
        opp_score = opp_dist * 2

        # Obstacle proximity penalty (cheap).
        obs_pen = 0
        for ex, ey in obstacles:
            d = cheb(nx, ny, ex, ey)
            if d == 0:
                obs_pen = -10**12
                break
            if d == 1:
                obs_pen -= 2

        total = res_score + opp_score + move_bias + obs_pen
        if total > best[2] or (total == best[2] and (dx, dy) < (best[0], best[1])):
            best = [dx, dy, total]

    return [int(best[0]), int(best[1])]