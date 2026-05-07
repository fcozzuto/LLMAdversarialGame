def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int):
                obs.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_val = -10**18

    # If opponent is closer, we prefer a resource where we are not behind; else we still race the best available.
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not free(nx, ny):
            continue

        immediate = 1 if any(nx == rx and ny == ry for rx, ry in resources) else 0
        val = immediate * 10**6

        # Evaluate the best resource after this move.
        local_best = -10**18
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            gain = do - ds  # positive means we arrive earlier than opponent (in cheb steps)
            # Prefer taking when we can get ahead, otherwise minimize being behind while staying fast.
            cand = gain * 2000 - ds * 3 + (1 if ds == 1 else 0)
            # If we are far behind, downweight heavily to avoid dead-end chases.
            if gain < 0:
                cand -= (-gain) * 800
            if cand > local_best:
                local_best = cand

        val += local_best

        # Small deterrent: don't move into squares that are more "central" for opponent unless beneficial.
        if (nx, ny) in obs:
            val -= 10**12
        if ox == nx or oy == ny:
            # encourage lateral/vertical progress slightly
            val += 5

        if val > best_val:
            best_val = val
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]