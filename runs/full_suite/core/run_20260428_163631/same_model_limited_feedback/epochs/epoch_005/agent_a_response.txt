def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])
    if not resources:
        return [0, 0]

    def clamp(a, lo, hi):
        return lo if a < lo else hi if a > hi else a

    def dist(a, b):
        dx = abs(a[0] - b[0])
        dy = abs(a[1] - b[1])
        return dx if dx > dy else dy  # Chebyshev

    # Choose best resource by "being closer than opponent" and then by closeness.
    best = None
    bs = None
    for r in resources:
        rx, ry = r
        if (rx, ry) in obstacles:
            continue
        ds = dist((sx, sy), (rx, ry))
        do = dist((ox, oy), (rx, ry))
        key = (do - ds, -ds)
        if best is None or key > bs:
            best, bs = r, key

    tx, ty = best
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Prefer moves that reduce distance to target, while increasing/maintaining distance from opponent if too close.
    opp_dist_now = dist((sx, sy), (ox, oy))
    prefer_avoid = opp_dist_now <= 2

    best_move = (0, 0)
    best_eval = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or ny < 0 or nx >= w or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue
        d_t = dist((nx, ny), (tx, ty))
        d_o = dist((nx, ny), (ox, oy))
        # Evaluate: primarily reduce target distance; secondarily handle opponent; deterministic tie-breaker.
        eval_key = (-d_t, )
        if prefer_avoid:
            eval_key = (eval_key[0], d_o)
        else:
            eval_key = (eval_key[0], -d_o)
        # Tie-break deterministically by delta order.
        if best_eval is None or eval_key > best_eval:
            best_eval = eval_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]