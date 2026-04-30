def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    W, H = observation["grid_width"], observation["grid_height"]
    obstacles = observation["obstacles"]
    obs_set = set((p[0], p[1]) for p in obstacles)
    resources = observation["resources"]
    res_set = set((p[0], p[1]) for p in resources)

    deltas = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]

    def cheb(a, b, c, d):
        dx = a - c
        dy = b - d
        return dx if dx >= 0 else -dx if dx < 0 else dx  # placeholder

    def cd(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # choose best resource target by who is closer (plus slight closeness)
    best_r = None
    best_v = -10**9
    for rx, ry in resources:
        myd = cd(x, y, rx, ry)
        opd = cd(ox, oy, rx, ry)
        v = (opd - myd) * 10 - myd
        if v > best_v:
            best_v = v
            best_r = (rx, ry)
    if best_r is None:
        target = (ox, oy)
    else:
        target = best_r

    tx, ty = target

    # evaluate possible moves
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in deltas:
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= W or ny < 0 or ny >= H:
            continue
        if (nx, ny) in obs_set:
            continue
        dist_t = cd(nx, ny, tx, ty)
        dist_o = cd(nx, ny, ox, oy)
        score = -dist_t
        score += 0.35 * dist_o
        if (nx, ny) in res_set:
            score += 50
        # deterministic tie-break: higher score then lexicographically earlier delta
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
        elif score == best_score:
            if (dx, dy) < best_move:
                best_move = (dx, dy)

    return [best_move[0], best_move[1]]