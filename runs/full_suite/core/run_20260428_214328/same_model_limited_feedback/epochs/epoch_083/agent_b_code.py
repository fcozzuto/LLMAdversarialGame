def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set((p[0], p[1]) for p in observation["obstacles"])

    def in_bounds(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        if dx < 0: dx = -dx
        if dy < 0: dy = -dy
        return dx + dy

    deltas = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    if not resources:
        return [0, 0]

    # Target: prioritize resources we can reach sooner than the opponent (deny).
    best_r = None
    best_val = None
    for r in resources:
        d_s = dist((sx, sy), r)
        d_o = dist((ox, oy), r)
        val = d_s - 0.9 * d_o
        if best_val is None or val < best_val:
            best_val = val
            best_r = r

    tx, ty = best_r

    # If we are far from all resources, just drift toward the best target; otherwise be denser in blocking.
    turns = observation.get("turn_index", 0)
    deny_weight = 0.9 if turns > 1 else 0.7

    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not in_bounds(nx, ny):
            continue
        if (nx, ny) in obstacles:
            continue

        d_new = dist((nx, ny), (tx, ty))
        # Approximate "opponent pressure": how their distance changes to the same target.
        # If opponent is already closer, we bias more toward denying.
        d_opp = dist((ox, oy), (tx, ty))
        pressure = 0.0
        if d_opp <= d_new:
            pressure = (d_new - d_opp)

        # Obstacle proximity penalty (discourages hugging obstacles).
        prox = 0
        for ax in (-1, 0, 1):
            for ay in (-1, 0, 1):
                if ax == 0 and ay == 0:
                    continue
                xx, yy = nx + ax, ny + ay
                if in_bounds(xx, yy) and (xx, yy) in obstacles:
                    prox += 1

        score = (d_new + deny_weight * max(0, pressure) + 0.8 * prox)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]