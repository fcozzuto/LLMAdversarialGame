def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obs

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def best_target_for(posx, posy):
        # Choose a resource that we can reach relatively better than opponent, then by our distance.
        best = None
        for rx, ry in resources:
            if (rx, ry) in obs:
                continue
            sd = cheb(posx, posy, rx, ry)
            od = cheb(ox, oy, rx, ry)
            key = (od - sd, -sd, -rx, -ry)  # deterministic
            if best is None or key > best[0]:
                best = (key, (rx, ry), sd, od)
        return best[1], best[2], best[3]

    if not resources:
        # Head to maximize separation from opponent and avoid obstacles.
        best = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                nx, ny = sx, sy
            v = cheb(nx, ny, ox, oy)
            key = (v, -nx, -ny)
            if best is None or key > best[0]:
                best = (key, dx, dy)
        return [best[1], best[2]]

    # Choose move that maximizes immediate improvement for the best contested target.
    best_move = (0, 0)
    best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            nx, ny = sx, sy
        target, sd, od = best_target_for(nx, ny)
        tr, ty = target
        my_d = cheb(nx, ny, tr, ty)
        opp_d = cheb(ox, oy, tr, ty)
        # Prefer larger advantage, then smaller my distance, then deterministic by move.
        key = (opp_d - my_d, -my_d, -tr, -ty, -dx, -dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]