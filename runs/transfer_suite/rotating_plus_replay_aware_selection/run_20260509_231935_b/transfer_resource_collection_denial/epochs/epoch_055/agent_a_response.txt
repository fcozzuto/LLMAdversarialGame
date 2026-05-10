def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    res = [(p[0], p[1]) for p in resources if p and len(p) >= 2]
    if not res:
        return [0, 0]
    obs = set((p[0], p[1]) for p in obstacles if p and len(p) >= 2)

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def dist_cheb(a, b):
        dx = a[0] - b[0]
        if dx < 0: dx = -dx
        dy = a[1] - b[1]
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Prefer resources that we can reach sooner, but also avoid giving the opponent an easy pickup.
    alpha = 0.35  # weight of opponent distance

    best_move = [0, 0]
    best_score = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obs:
            continue

        # Score by best available resource after this move (lower is better).
        move_best = None
        for rx, ry in res:
            if (rx, ry) in obs:
                continue
            d_self = dist_cheb((nx, ny), (rx, ry))
            d_opp = dist_cheb((ox, oy), (rx, ry))
            # Encourage capturing while deprioritizing resources close to opponent.
            score = d_self - alpha * d_opp
            # Strongly discourage moves that stay when any pickup is possible nearby.
            if dx == 0 and dy == 0:
                score += 0.05
            if move_best is None or score < move_best:
                move_best = score

        if move_best is None:
            continue

        # Deterministic tie-break: prefer moves that reduce our distance to the chosen "best" resource,
        # then prefer positive dx, then positive dy, then staying last.
        if best_score is None or move_best < best_score:
            best_score = move_best
            best_move = [dx, dy]
        elif move_best == best_score:
            if dx > best_move[0] or (dx == best_move[0] and dy > best_move[1]):
                best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]