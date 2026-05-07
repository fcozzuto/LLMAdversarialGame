def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx >= dy else dy

    def step_to(tx, ty):
        dx_dir = 0 if tx == sx else (1 if tx > sx else -1)
        dy_dir = 0 if ty == sy else (1 if ty > sy else -1)
        cand = []
        for dx0 in (-1, 0, 1):
            for dy0 in (-1, 0, 1):
                nx, ny = sx + dx0, sy + dy0
                if legal(nx, ny):
                    cand.append((dx0, dy0))
        if not cand:
            return [0, 0]
        # Score move: reduce our distance to target, and (slightly) increase opponent distance to target.
        best = None
        best_val = None
        for dx0, dy0 in cand:
            nx, ny = sx + dx0, sy + dy0
            self_d = cheb(nx, ny, tx, ty)
            opp_d = cheb(ox, oy, tx, ty)
            # Prefer moves that also head in the intended direction.
            align = (1 if dx0 == dx_dir else 0) + (1 if dy0 == dy_dir else 0)
            val = (self_d * 100) - (opp_d * 2) - align
            if best_val is None or val < best_val:
                best_val = val
                best = (dx0, dy0)
        return [best[0], best[1]] if best else [0, 0]

    if not resources:
        tx, ty = (w // 2, h // 2)
        return step_to(tx, ty)

    # Pick a resource where we can beat the opponent in distance; otherwise, deny the closest ones to them.
    chosen = None
    chosen_score = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Primary: maximize (od - sd). Secondary: minimize our distance to finish sooner.
        score = (sd - od, sd, abs(rx - (w // 2)) + abs(ry - (h // 2)))
        if chosen_score is None or score < chosen_score:
            chosen_score = score
            chosen = (rx, ry)

    if chosen is None:
        return [0, 0]
    tx, ty = chosen

    # If target is adjacent but blocked in our best direction, try a nearby alternative step by local steering.
    return step_to(tx, ty)