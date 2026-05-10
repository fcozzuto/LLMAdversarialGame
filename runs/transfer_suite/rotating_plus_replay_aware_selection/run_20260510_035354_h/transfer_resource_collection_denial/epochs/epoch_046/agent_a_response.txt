def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            obs.add((int(p[0]), int(p[1])))
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            x, y = int(p[0]), int(p[1])
            if (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def cheb(a, b, c, d):
        dx = a - c
        if dx < 0: dx = -dx
        dy = b - d
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    best_score = None
    best_move = [0, 0]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Prefer grabbing immediate resource; otherwise go toward the best "stealable" resource.
        if (nx, ny) in res:
            return [dx, dy]

        # Score the best target given my prospective position, penalizing targets closer to opponent.
        local_best = None
        for rx, ry in res:
            d_me = cheb(nx, ny, rx, ry)
            d_opp = cheb(ox, oy, rx, ry)
            score = d_me - 0.35 * d_opp
            if local_best is None or score < local_best:
                local_best = score
        # Add a tiny deterministic preference for moves that reduce distance to current "best" target.
        # (local_best corresponds to that best target, but we use it only comparatively.)
        step_pen = 0.0
        if dx != 0 or dy != 0:
            # Encourage progress: slight penalty for staying
            step_pen = 0.01
        score2 = local_best + step_pen + (0.0001 * (abs(ox - nx) + abs(oy - ny)))
        if best_score is None or score2 < best_score or (score2 == best_score and (dx, dy) < (best_move[0], best_move[1])):
            best_score = score2
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]