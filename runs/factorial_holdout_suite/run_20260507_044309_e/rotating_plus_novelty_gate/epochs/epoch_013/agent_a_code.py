def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", [])
    obstacles = set((p[0], p[1]) for p in observation.get("obstacles", []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def man(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx + dy

    if not resources:
        return [0, 0]

    best_rx = resources[0][0]
    best_ry = resources[0][1]
    best_score = None

    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        our_d = man(sx, sy, rx, ry)
        opp_d = man(ox, oy, rx, ry)
        # Prefer resources where we're closer; else just the closest to us.
        score = (opp_d - our_d, -our_d)
        if best_score is None or score > best_score or (score == best_score and (rx, ry) < (best_rx, best_ry)):
            best_score = score
            best_rx, best_ry = rx, ry

    best_move = (0, 0)
    best_eval = None
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            our_d = man(nx, ny, best_rx, best_ry)
            opp_d = man(ox, oy, best_rx, best_ry)
            # Primary: get closer to target; Secondary: widen gap vs opponent for that target; Tertiary: closer to any resource.
            res_d = min(man(nx, ny, r[0], r[1]) for r in resources if (r[0], r[1]) not in obstacles)
            evalv = (-our_d, (opp_d - our_d), -res_d, dx, dy)
            if best_eval is None or evalv > best_eval:
                best_eval = evalv
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]