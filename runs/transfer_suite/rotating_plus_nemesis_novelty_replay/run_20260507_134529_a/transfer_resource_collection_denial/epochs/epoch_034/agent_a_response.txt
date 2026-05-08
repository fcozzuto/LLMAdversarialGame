def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def score_pos(px, py):
        if not resources:
            return 0
        best_margin = -10**9
        sum_margin = 0
        closest_ds = 10**9
        closest_r = None
        for rx, ry in resources:
            ds = cheb(px, py, rx, ry)
            do = cheb(ox, oy, rx, ry)
            margin = do - ds  # positive if we can reach earlier than opponent
            if margin > best_margin:
                best_margin = margin
                closest_r = (rx, ry)
            if ds < closest_ds:
                closest_ds = ds
            # emphasize winning contest, penalize losing
            if ds <= do:
                sum_margin += (margin + 1) * 10 - ds
            else:
                sum_margin -= (do - ds + 1) * 6
        # add strong push toward the best winning target (ties favor closer arrival)
        bx, by = closest_r if closest_r is not None else (sx, sy)
        tie_bias = -0.5 * cheb(px, py, bx, by) - 0.05 * cheb(px, py, ox, oy)
        return sum_margin * 100 + best_margin * 50 + tie_bias

    best_move = [0, 0]
    best_val = -10**18
    # Deterministic tie-break: smaller dx, then smaller dy in dirs order
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        val = score_pos(nx, ny)
        if val > best_val:
            best_val = val
            best_move = [dx, dy]
    return best_move