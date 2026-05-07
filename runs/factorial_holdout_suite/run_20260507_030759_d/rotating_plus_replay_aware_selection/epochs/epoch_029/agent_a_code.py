def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0:
            dx = -dx
        dy = ay - by
        if dy < 0:
            dy = -dy
        return dx + dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    def best_step_towards(px, py, tx, ty):
        best = [0, 0]
        bestd = 10**9
        for dx, dy in moves:
            nx, ny = px + dx, py + dy
            if not ok(nx, ny):
                continue
            d = man(nx, ny, tx, ty)
            if d < bestd:
                bestd = d
                best = [dx, dy]
        return best

    best_move = [0, 0]
    best_val = -10**30

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        cur_best = -10**30
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = man(nx, ny, rx, ry)
            # predict opponent greedy step for this same resource
            odx, ody = best_step_towards(ox, oy, rx, ry)
            nvox, nvoy = ox + odx, oy + ody
            do = man(nvox, nvoy, rx, ry)
            lead = do - ds  # positive if we are closer than opponent next
            # prioritize securing a resource soon, and maximizing advantage
            val = lead * 1000 - ds
            if val > cur_best:
                cur_best = val
        if cur_best > best_val:
            best_val = cur_best
            best_move = [dx, dy]

    return [best_move[0], best_move[1]]