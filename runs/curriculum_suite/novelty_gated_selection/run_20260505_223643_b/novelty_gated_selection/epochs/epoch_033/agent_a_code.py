def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0), (0, 0), (1, 0),
             (-1, 1), (0, 1), (1, 1)]

    def man(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx + dy

    def nearest_dist(px, py):
        best = 10**9
        for rx, ry in resources:
            d = man(px, py, rx, ry)
            if d < best:
                best = d
        return best

    opp_nearest = nearest_dist(ox, oy)

    best_move = [0, 0]
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue

        my_nearest = nearest_dist(nx, ny)
        adv = opp_nearest - my_nearest

        opp_close = man(nx, ny, ox, oy)
        # Prefer winning races, but also keep spacing from sweep-like opponent.
        score = 2.0 * adv - 0.35 * opp_close + 0.02 * my_nearest

        # Small deterministic tie-breaker: prefer staying closer to own resources if equal,
        # then prefer lower dx, then lower dy.
        if score > best_score or (score == best_score and (my_nearest < nearest_dist(best_move[0] + sx, best_move[1] + sy) or
                                                           (my_nearest == nearest_dist(best_move[0] + sx, best_move[1] + sy) and (dx < best_move[0] or (dx == best_move[0] and dy < best_move[1]))))):
            best_score = score
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]