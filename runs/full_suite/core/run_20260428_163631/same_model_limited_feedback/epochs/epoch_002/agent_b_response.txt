def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation["obstacles"]
    obs_set = set((x, y) for x, y in obstacles)
    resources = observation["resources"]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    if resources:
        best_r = None
        best_val = -10**9
        for rx, ry in resources:
            if (rx, ry) in obs_set:
                continue
            ds = dist((sx, sy), (rx, ry))
            do = dist((ox, oy), (rx, ry))
            val = (do - ds) * 10 - ds  # prioritize being closer than opponent, then nearer
            if val > best_val:
                best_val = val
                best_r = (rx, ry)
        tx, ty = best_r
    else:
        tx, ty = w // 2, h // 2

    opp_dist_to_target = dist((ox, oy), (tx, ty))
    self_dist_to_target = dist((sx, sy), (tx, ty))

    moves = [(0, 0), (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = None
    best_score = 10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs_set:
            continue
        d_after = dist((nx, ny), (tx, ty))
        # If opponent is closer, add a mild "intercept" bias by preferring steps that increase opponent distance.
        d_opp_after = dist((ox, oy), (tx, ty))
        bias = 0
        if opp_dist_to_target < self_dist_to_target:
            # crude intercept: also prefer moving toward the line from opponent to target
            vx1, vy1 = tx - ox, ty - oy
            vx2, vy2 = nx - ox, ny - oy
            dot = vx1 * vx2 + vy1 * vy2
            bias = -0.1 * dot
        score = d_after * 3 + (0 if (nx, ny) == (tx, ty) else 0) + bias
        if score < best_score:
            best_score = score
            best = (dx, dy)

    if best is None:
        return [0, 0]
    return [int(best[0]), int(best[1])]