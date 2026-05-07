def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obstacles = obstacles_raw if isinstance(obstacles_raw, set) else set(tuple(p) for p in obstacles_raw)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if not resources:
        return [0, 0]

    best_m = (0, 0)
    best_val = -10**18
    eps = 1e-6

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            val = -10**12
        else:
            # pick a target resource maximizing my advantage after moving
            my_best = -10**18
            opp_best = 10**18
            for rx, ry in resources:
                ds = cheb(nx, ny, rx, ry)
                do = cheb(ox, oy, rx, ry)
                # advantage: I want do - ds large; also if close, prioritize quickly collecting
                adv = do - ds
                collect = -ds * 0.05
                # deny pressure: if opponent is much closer to some resource, bias against it
                deny = -max(0, do - ds) * 0.02
                score = adv + collect + deny
                if score > my_best or (score == my_best and (ds < opp_best)):
                    my_best = score
                    opp_best = ds
            # add slight bias to move toward center-ish to avoid oscillation
            center_bias = -((nx - (w - 1) / 2.0) ** 2 + (ny - (h - 1) / 2.0) ** 2) * eps
            val = my_best + center_bias
        if val > best_val:
            best_val = val
            best_m = (dx, dy)

    return [best_m[0], best_m[1]]