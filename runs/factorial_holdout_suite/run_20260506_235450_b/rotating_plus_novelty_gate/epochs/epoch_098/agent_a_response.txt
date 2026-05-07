def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_mv = (0, 0)
    best_val = None

    # Prefer: immediate pickup, then states where we are earlier than opponent for some resource, else progress to closest.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        pickup = 1.0 if (nx, ny) in res else 0.0

        best_self_gap = None
        best_self_dist = None
        for tx, ty in res:
            ds = cheb(nx, ny, tx, ty)
            do = cheb(ox, oy, tx, ty)
            gap = ds - do  # smaller is better (we're earlier when gap is smaller/negative)
            if best_self_gap is None or gap < best_self_gap or (gap == best_self_gap and ds < best_self_dist):
                best_self_gap = gap
                best_self_dist = ds

        # Secondary: avoid moves that let opponent be strictly earlier for all resources.
        # Use a mild time pressure to commit as game progresses.
        tr = observation.get("turns_remaining", 0)
        time_weight = 1.0 if tr is None else (0.5 if tr > 20 else 1.2)
        val = pickup * 1000 + (-best_self_gap) * time_weight - best_self_dist * 0.05

        if best_val is None or val > best_val + 1e-12:
            best_val = val
            best_mv = (dx, dy)
    return [best_mv[0], best_mv[1]]