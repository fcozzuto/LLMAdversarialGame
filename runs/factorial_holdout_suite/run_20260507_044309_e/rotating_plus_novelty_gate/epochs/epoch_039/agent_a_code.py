def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles
    def md(x1, y1, x2, y2):
        dx = x1 - x2; dx = dx if dx >= 0 else -dx
        dy = y1 - y2; dy = dy if dy >= 0 else -dy
        return dx + dy
    resources = observation.get("resources") or []
    valid = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            valid.append((dx, dy, nx, ny))
    if not valid:
        return [0, 0]
    if not resources:
        tx, ty = w // 2, h // 2
        best = None; bd = 10**9; bi = 10**9
        for i, (dx, dy, nx, ny) in enumerate(valid):
            d = md(nx, ny, tx, ty)
            if d < bd or (d == bd and i < bi):
                best = (dx, dy); bd = d; bi = i
        return [best[0], best[1]]
    best_move = (0, 0); best_val = -10**18; best_t = 10**18; best_i = 10**9
    for i, (dx, dy, nx, ny) in enumerate(valid):
        my_best = 10**9
        # Estimate best target "swing": prefer targets where we arrive earlier than opponent
        # For each target, compute score = (opp_steps - my_steps), tie by smaller my_steps then index.
        local_best = -10**18; local_t = 10**18
        for rx, ry in resources:
            my_steps = md(nx, ny, rx, ry)
            opp_steps = md(ox, oy, rx, ry)
            swing = opp_steps - my_steps
            if swing > local_best or (swing == local_best and my_steps < local_t) or (swing == local_best and my_steps == local_t and rx + 131 * ry < my_best):
                local_best = swing
                local_t = my_steps
                my_best = rx + 131 * ry
        # Small preference to reduce absolute time-to-resource once swing is comparable
        val = local_best * 100 - local_t
        if val > best_val or (val == best_val and local_t < best_t) or (val == best_val and local_t == best_t and i < best_i):
            best_val = val; best_t = local_t; best_move = (dx, dy); best_i = i
    return [int(best_move[0]), int(best_move[1])]