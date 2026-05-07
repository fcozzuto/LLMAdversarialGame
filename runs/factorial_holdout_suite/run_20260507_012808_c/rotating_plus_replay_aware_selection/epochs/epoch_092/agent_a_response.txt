def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (0, 0)
        bestd = 10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                d = cheb(nx, ny, tx, ty)
                if d < bestd or (d == bestd and (dx, dy) < tuple(best)):
                    bestd = d
                    best = [dx, dy]
        return best

    res = [tuple(r) for r in resources]
    dirs_sorted = sorted(dirs, key=lambda t: (t[0] * 2 + t[1], t))
    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in dirs_sorted:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        local_best = -10**18
        for rx, ry in res:
            our_d = cheb(nx, ny, rx, ry)
            opp_d = cheb(ox, oy, rx, ry)
            # Prefer resources we are closer to; penalize if opponent is much closer.
            # Also slightly prefer nearer targets to avoid dithering.
            val = (opp_d - our_d) * 10 - our_d
            if val > local_best:
                local_best = val
        # Secondary tie-break: prefer to keep moving toward some resource (less opp advantage globally).
        # Use best possible resource margin based on current position.
        cur_best = -10**18
        for rx, ry in res:
            our_d0 = cheb(sx, sy, rx, ry)
            opp_d0 = cheb(ox, oy, rx, ry)
            v0 = (opp_d0 - our_d0) * 10 - our_d0
            if v0 > cur_best:
                cur_best = v0
        score = local_best + (cur_best - local_best) * 0.01
        if score > best_score or (score == best_score and (dx, dy) < tuple(best_move)):
            best_score = score
            best_move = [dx, dy]
    return best_move