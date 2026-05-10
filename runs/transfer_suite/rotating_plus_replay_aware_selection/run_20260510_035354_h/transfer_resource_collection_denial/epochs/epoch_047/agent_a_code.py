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
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    best = None
    best_move = [0, 0]

    for mdx, mdy in moves:
        nx, ny = sx + mdx, sy + mdy
        if not valid(nx, ny):
            continue

        # Immediate pickup dominates
        if (nx, ny) in obs:
            continue

        key_pick = 0
        if (nx, ny) in res:
            key_pick = 1

        # Choose target based on who can reach it first
        best_t = None
        best_t_key = None
        for tx, ty in res:
            d_self = cheb(nx, ny, tx, ty)
            d_opp = cheb(ox, oy, tx, ty)
            # Prefer targets we can reach no worse than opponent; then minimize distance
            t_key = (0 if d_self <= d_opp else 1, d_self, abs(tx - nx) + abs(ty - ny), tx, ty)
            if best_t_key is None or t_key < best_t_key:
                best_t_key = t_key
                best_t = (tx, ty)

        # Evaluate: primarily get closer / win pickup race; secondarily discourage blocking with obstacle-adjacent steps
        tx, ty = best_t
        d_after = cheb(nx, ny, tx, ty)
        # obstacle proximity penalty (deterministic small)
        adj_obs = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                ex, ey = nx + ax, ny + ay
                if 0 <= ex < w and 0 <= ey < h and (ex, ey) in obs:
                    adj_obs += 1
        move_key = (-key_pick, best_t_key[0], best_t_key[1], d_after, adj_obs, mdx, mdy)
        if best is None or move_key < best:
            best = move_key
            best_move = [mdx, mdy]

    return [int(best_move[0]), int(best_move[1])]