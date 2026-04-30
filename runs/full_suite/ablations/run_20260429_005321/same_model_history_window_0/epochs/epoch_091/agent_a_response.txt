def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((x, y) for x, y in observation["obstacles"])
    resources = observation["resources"]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def dist(a, b):
        ax, ay = a
        bx, by = b
        dx = ax - bx
        dy = ay - by
        return abs(dx) + abs(dy)

    # Choose a target resource that favors us: maximize (opp_dist - self_dist), then minimize self_dist, then lexicographic.
    if resources:
        best = None
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            sd = dist((sx, sy), (rx, ry))
            od = dist((ox, oy), (rx, ry))
            advantage = od - sd
            key = (-advantage, sd, rx, ry)
            if best is None or key < best[0]:
                best = (key, (rx, ry))
        tx, ty = best[1]
    else:
        tx, ty = (w // 2, h // 2)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    # Deterministic preference order slightly shifts based on turn parity to avoid cycles.
    if observation.get("turn_index", 0) % 2:
        moves = [(-1, 0), (0, -1), (1, 0), (0, 1), (0, 0), (-1, -1), (1, -1), (-1, 1), (1, 1)]

    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Prefer moves that reduce self distance to target, and avoid getting too close to opponent unless it helps us.
        self_d = dist((nx, ny), (tx, ty))
        opp_close = -dist((nx, ny), (ox, oy))  # larger when closer
        # Also encourage stepping onto a resource.
        res_bonus = 0
        if resources and (nx, ny) in set((x, y) for x, y in resources):
            res_bonus = -20
        score = (self_d + 0.2 * opp_close + res_bonus, -abs(dx) - abs(dy), nx, ny)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]