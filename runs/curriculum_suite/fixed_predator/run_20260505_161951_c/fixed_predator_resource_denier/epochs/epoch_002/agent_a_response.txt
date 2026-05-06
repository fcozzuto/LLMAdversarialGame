def choose_move(observation):
    x, y = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = observation.get("obstacles", [])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)

    obstacle_set = set((a, b) for a, b in obstacles)
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def in_bounds(nx, ny):
        return 0 <= nx < w and 0 <= ny < h

    def cheb(a, b, c, d):
        da = abs(a - c)
        db = abs(b - d)
        return da if da > db else db

    def step_allowed(dx, dy):
        nx, ny = x + dx, y + dy
        if not in_bounds(nx, ny):
            return False
        return (nx, ny) not in obstacle_set

    if not resources:
        # chase opponent weakly while avoiding obstacles
        best = (0, 0)
        best_score = -10**9
        for dx, dy in dirs:
            if not step_allowed(dx, dy):
                continue
            nx, ny = x + dx, y + dy
            d_opp = cheb(nx, ny, ox, oy)
            d_home = cheb(nx, ny, w - 1 - ox, h - 1 - oy)
            score = -d_opp - 0.1 * d_home
            if score > best_score or (score == best_score and (dx, dy) < best):
                best_score = score
                best = (dx, dy)
        return [best[0], best[1]]

    # choose best target resource deterministically
    best_t = resources[0]
    best_val = -10**18
    for rx, ry in resources:
        sd = cheb(x, y, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # prefer resources where we have advantage; also prefer closer for quick capture
        val = (od - sd) * 1000 - sd
        if val > best_val or (val == best_val and (sd, rx, ry) < (cheb(x, y, best_t[0], best_t[1]), best_t[0], best_t[1])):
            best_val = val
            best_t = (rx, ry)

    tx, ty = best_t

    # 1-step lookahead: for each possible move, score based on our progress and relative pressure
    best = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        if not step_allowed(dx, dy):
            continue
        nx, ny = x + dx, y + dy

        sd_now = cheb(x, y, tx, ty)
        sd_next = cheb(nx, ny, tx, ty)

        # opponent pressure: assume opponent moves similarly toward same target (approx by distance after our move)
        od_next_est = cheb(ox, oy, tx, ty)

        # strong preference: reduce our distance; second: widen opponent gap
        progress = sd_now - sd_next
        gap = (od_next_est - sd_next)

        # small obstacle-aware penalty for being stuck far from any resource (discourage wasted moves)
        min_res_sd = 10**9
        for rx, ry in resources:
            d = cheb(nx, ny, rx, ry)
            if d < min_res_sd:
                min_res_sd = d

        score = progress * 2000 + gap * 50 - min_res_sd

        if score > best_score or (score == best_score and (dx, dy) < best):
            best_score = score
            best = (dx, dy)

    return [best[0], best[1]]