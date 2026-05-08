def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    if not resources:
        return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)]

    best = None
    # One-step lookahead: pick move that maximizes your ability to be at least as close as opponent
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        if (nx, ny) in obstacles:
            continue

        best_adv = None
        win_count = 0
        best_t_self = None
        for rx, ry in resources:
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            adv = do - ds  # positive => you are closer (or tied) than opponent
            if best_adv is None or adv > best_adv:
                best_adv = adv
            if ds <= do:
                win_count += 1
            if best_t_self is None or ds < best_t_self:
                best_t_self = ds

        # Prefer higher immediate advantage, then more resources you "beat", then move that shortens your closest path
        key = (best_adv, win_count, -best_t_self, -dx, -dy)
        if best is None or key > best[0]:
            best = (key, [dx, dy])

    return best[1]