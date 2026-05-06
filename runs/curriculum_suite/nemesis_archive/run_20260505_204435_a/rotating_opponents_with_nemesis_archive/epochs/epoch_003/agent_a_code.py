def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = set((p[0], p[1]) for p in obstacles)
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0: pass
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
                    d = max(abs(nx - cx), abs(ny - cy))
                    key = (d, abs(nx - ox) + abs(ny - oy), dx, dy)
                    if best is None or key < best[0]:
                        best = (key, dx, dy)
        return [best[1], best[2]] if best else [0, 0]

    def step(ax, ay, bx, by):
        return max(abs(ax - bx), abs(ay - by))

    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            continue
        # Evaluate best resource we can "win" from this next position
        best_adv = None
        best_t = None
        for rx, ry in resources:
            ss = step(nx, ny, rx, ry)
            os = step(ox, oy, rx, ry)
            adv = os - ss  # positive means we reach earlier
            if best_adv is None or (adv, -ss, -os) > (best_adv[0], -best_adv[1], -best_adv[2]):
                best_adv = (adv, ss, os)
                best_t = (rx, ry)
        # Prefer winning captures; otherwise minimize being behind and keep safe from immediate competition
        adv, ss, os = best_adv
        # Slight center/continuation bias
        center_bias = max(abs(nx - (w - 1) / 2), abs(ny - (h - 1) / 2))
        opp_close = max(0, 3 - max(abs(nx - ox), abs(ny - oy)))
        # Key: maximize adv, then minimize our steps, then minimize opponent steps, then center_bias, then dx/dy
        key = (-adv, ss, os, center_bias, opp_close, dx, dy, best_t[0], best_t[1])
        if best is None or key < best[0]:
            best = (key, dx, dy)
    if best is None:
        return [0, 0]
    return [best[1], best[2]]