def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    if not resources:
        tx, ty = w // 2, h // 2
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            for adx, ady in ((dx, 0), (0, dy), (0, 0)):
                nx, ny = sx + adx, sy + ady
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    return [adx, ady]
            return [0, 0]

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def best_target_value(x, y):
        bestv = -10**18
        for rx, ry in resources:
            if (rx, ry) in obstacles:
                continue
            ds = cheb(x, y, rx, ry)
            do = cheb(ox, oy, rx, ry)
            lead = do - ds  # positive => we reach earlier
            center = cheb(rx, ry, w // 2, h // 2)
            v = lead * 1000 - ds * 5 - center
            if v > bestv:
                bestv = v
        return bestv

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]
    best = None
    bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        v = best_target_value(nx, ny)
        # small tie-break: prefer staying closer to opponent-competition (bigger lead first already),
        # then reduce own distance to best target by slight lookahead with current position
        if v > bestv:
            bestv = v
            best = (dx, dy)
    if best is None:
        return [0, 0]
    return [best[0], best[1]]