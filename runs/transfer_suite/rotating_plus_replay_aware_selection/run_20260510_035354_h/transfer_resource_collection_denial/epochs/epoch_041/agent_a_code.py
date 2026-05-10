def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            t = (int(p[0]), int(p[1]))
            if t not in obs:
                res.append(t)
    if not res:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    best = None
    best_key = (-10**18, 10**9, 10**9)

    # Prefer capturing contested resources where we become closer (or already closest).
    # Also, lightly prefer moving toward the single best target.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue

        immediate = 1 if (nx, ny) in res else 0
        total_gain = 0
        best_dist = 10**9
        for rx, ry in res:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # Strongly prefer resources where we are closer after the move.
            delta = opd - myd  # positive => we are closer
            # Bias toward nearer targets.
            if delta > 0:
                gain = 5000 * (1 + delta) - 3 * myd
            else:
                gain = -2000 * (1 + (-delta)) - 2 * myd
            if myd < best_dist:
                best_dist = myd
            total_gain += gain

        key = (total_gain + 20000 * immediate, -best_dist, -cheb(nx, ny, sx, sy))
        if key > best_key:
            best_key = key
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]