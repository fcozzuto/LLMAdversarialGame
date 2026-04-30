def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
    resources = []
    for p in (observation.get("resources") or []):
        if p and len(p) >= 2:
            t = (int(p[0]), int(p[1]))
            if t not in obstacles:
                resources.append(t)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def safe(nx, ny):
        return 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles

    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not safe(nx, ny): 
                continue
            d = cheb(nx, ny, tx, ty)
            k = (d, abs(nx - tx) + abs(ny - ty), dx, dy)
            if best is None or k < best[0]:
                best = (k, [dx, dy])
        return best[1] if best else [0, 0]

    # Evaluate each move by the best resource we could pursue next, measuring advantage vs opponent.
    best_move = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        my_after_best = None
        opp_at_that = None
        res_at_that = None
        # Choose resource that maximizes our immediate advantage; tie-break deterministically.
        for rx, ry in resources:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            gain = opd - myd
            if my_after_best is None:
                my_after_best = myd
                opp_at_that = opd
                res_at_that = (rx, ry, gain)
            else:
                # Prefer higher gain; then closer for us; then deterministic by coords.
                if (gain, -myd, -rx, -ry) > (res_at_that[2], -my_after_best, -res_at_that[0], -res_at_that[1]):
                    my_after_best = myd
                    opp_at_that = opd
                    res_at_that = (rx, ry, gain)
        rx, ry, gain = res_at_that
        # Primary: maximize gain; Secondary: minimize my distance; Tertiary: break ties by preferring resources nearer to center and lexicographic move.
        center_dist = abs(rx - (w - 1) / 2) + abs(ry - (h - 1) / 2)
        key = (-(gain), my_after_best, center_dist, dx, dy, rx, ry, opp_at_that)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move if best_move is not None else [0, 0]