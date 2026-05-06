def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obstacles = set(tuple(p) for p in observation.get("obstacles", []))
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    # Pick best target: prefer we can secure (arrive no later), then shortest secure distance,
    # else race for closest with a tie-break that discourages letting opponent get it sooner.
    best_key = None
    best_r = resources[0]
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        secure = 0 if sd <= od else 1  # 0=prefer secure
        # Key fields: secure first, then our distance, then opponent margin, then coords
        key = (secure, sd, od - sd, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)
    rx, ry = best_r

    # Move selection: among legal next moves, maximize "advantage" for the chosen target,
    # and lightly reduce distance to nearest resource overall to keep progress.
    def nearest_dist(ax, ay):
        md = 10**9
        for x, y in resources:
            if (x, y) in obstacles:
                continue
            d = cheb(ax, ay, x, y)
            if d < md:
                md = d
        return md if md != 10**9 else cheb(ax, ay, rx, ry)

    opp_after_best = None  # deterministic, unused except for comparison
    cur_near = nearest_dist(sx, sy)
    best_move = (0, 0)
    best_score = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        my_d = cheb(nx, ny, rx, ry)
        op_d = cheb(ox, oy, rx, ry)
        # Primary: keep/extend ability to secure chosen resource.
        # Score: smaller my_d and larger (op_d - my_d) are better.
        secure_bonus = 0 if my_d <= op_d else 1
        near_after = nearest_dist(nx, ny)
        # Secondary: reduce threat of losing multiple turns (progress heuristic).
        score = (secure_bonus, my_d, -(op_d - my_d), near_after, dx, dy)
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]