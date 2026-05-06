def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0:
            ax = -ax
        ay = y1 - y2
        if ay < 0:
            ay = -ay
        return ax if ax >= ay else ay

    def pick_resource_score(x, y):
        # Higher is better for us: beat opponent (d_opp - d_me), then closer.
        best = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            d_me = cheb(x, y, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            rel = d_opp - d_me
            # Strongly prefer states where we can reach earlier than opponent.
            val = rel * 30 - d_me
            if val > best:
                best = val
        return best

    best_val = -10**18
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny) or (nx, ny) in obstacles:
            continue
        val = pick_resource_score(nx, ny)
        # Secondary: keep pressure near where opponent is aiming by also measuring relative advantage directly.
        # (Deterministic tie-breaker.)
        if val > best_val:
            best_val = val
            best_move = [dx, dy]
        elif val == best_val:
            # Prefer moves that reduce our distance to the opponent (more intercept power).
            if cheb(nx, ny, ox, oy) < cheb(sx, sy, ox, oy):
                best_move = [dx, dy]
    return best_move