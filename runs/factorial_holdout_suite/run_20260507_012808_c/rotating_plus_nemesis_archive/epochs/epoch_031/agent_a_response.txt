def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    # Pick a target we are likely to reach first: maximize (opp_dist - self_dist), then closest to us.
    if res:
        best_t = None
        best_key = None
        for tx, ty in res:
            sd = cheb(sx, sy, tx, ty)
            od = cheb(ox, oy, tx, ty)
            key = (-(od - sd), sd, tx, ty)  # minimize: negative margin? -> smallest od-sd => best
            if best_key is None or key < best_key:
                best_key = key
                best_t = (tx, ty)
        tx, ty = best_t
    else:
        tx, ty = ox, oy

    # Choose move that improves our time to target and keeps opponent farther from it.
    best_move = [0, 0]
    best = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        sd = cheb(nx, ny, tx, ty)
        od = cheb(ox, oy, tx, ty)
        # Prefer reduced self distance; break ties by increasing separation vs opponent.
        key = (sd, -(od - sd), nx, ny)
        if best is None or key < best:
            best = key
            best_move = [dx, dy]
    return best_move