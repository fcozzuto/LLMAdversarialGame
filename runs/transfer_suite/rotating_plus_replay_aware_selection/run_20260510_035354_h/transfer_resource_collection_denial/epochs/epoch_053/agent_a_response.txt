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
    seen = set()
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if (x, y) not in obs and (x, y) not in seen:
                seen.add((x, y))
                res.append((x, y))
    if not res:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    best_move = [0, 0]
    best_score = None

    # Choose the resource that gives us best race advantage, then move greedily to improve it.
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not valid(nx, ny):
            continue

        immediate = 1 if (nx, ny) in seen else 0
        # Score: prioritize immediate pickup, then win the race, then reduce our distance to target.
        # Tie-break deterministically by scanning resources in order.
        local_best = None
        local_best_key = None
        for tx, ty in res:
            ds = cheb(nx, ny, tx, ty)
            do = cheb(ox, oy, tx, ty)
            key = (0, 0, 0)
            # Higher is better: advantage + closeness; exact weights deterministic.
            advantage = (do - ds)  # positive means we can reach earlier/equal in fewer turns
            # Prefer larger advantage; if tied, prefer smaller ds; if tied, prefer nearer overall.
            key = (advantage, -ds, -(cheb(sx, sy, tx, ty)))
            if local_best_key is None or key > local_best_key:
                local_best_key = key
                local_best = tx, ty

        if local_best is None:
            continue

        dsx = cheb(nx, ny, local_best[0], local_best[1])
        dox = cheb(ox, oy, local_best[0], local_best[1])
        advantage = dox - dsx
        score = (immediate * 10**6) + (advantage * 10_000) + (-dsx * 100) + (-(nx - ox)*(nx - ox) - (ny - oy)*(ny - oy))
        if best_score is None or score > best_score:
            best_score = score
            best_move = [dxm, dym]

    return [int(best_move[0]), int(best_move[1])]