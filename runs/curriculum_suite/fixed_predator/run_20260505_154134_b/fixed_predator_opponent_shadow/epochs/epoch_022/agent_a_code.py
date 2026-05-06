def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # choose a target: prefer cells where we can arrive at least as fast as opponent, tie by closeness to opponent (deny).
    best_target = None
    best_key = None
    for cx, cy in resources:
        sd = cheb(sx, sy, cx, cy)
        od = cheb(ox, oy, cx, cy)
        key = (-(sd - od), -sd, od, cx, cy)  # larger is better: advantage first
        if best_key is None or key > best_key:
            best_key = key
            best_target = (cx, cy)
    if best_target is None:
        return [0, 0]
    tx, ty = best_target

    best_move = [0, 0]
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        ns = cheb(nx, ny, tx, ty)
        os = cheb(ox, oy, tx, ty)
        # intercept pressure: favor reducing our distance relative to opponent to the current best target
        rel = os - ns
        # obstacle proximity penalty (avoid trapping lanes): count blocked neighbors around next position
        block = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                px, py = nx + ax, ny + ay
                if (not inb(px, py)) or ((px, py) in obs):
                    block += 1
        # slight preference for moving toward any resource if not on the chosen one
        any_best = 0
        for rx, ry in resources:
            d = cheb(nx, ny, rx, ry)
            if any_best == 0 or d < any_best:
                any_best = d
        score = (rel, -ns, -block, -any_best, -abs(nx-ox), -abs(ny-oy), dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move