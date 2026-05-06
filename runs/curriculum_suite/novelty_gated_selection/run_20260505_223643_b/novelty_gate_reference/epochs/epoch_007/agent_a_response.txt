def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    best_score = -10**18
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        s = 0
        # choose best resource for this next cell
        local_best = -10**18
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # maximize advantage over opponent; tie-break by faster pickup
            val = 5 * (opd - myd) - myd
            if val > local_best:
                local_best = val
        s = local_best

        # small bias to head toward center lanes early/midgame (helps vs edge patrol)
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        dist_now = abs(x - cx) + abs(y - cy)
        dist_next = abs(nx - cx) + abs(ny - cy)
        s -= 0.1 * (dist_next - dist_now)

        if s > best_score:
            best_score = s
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]