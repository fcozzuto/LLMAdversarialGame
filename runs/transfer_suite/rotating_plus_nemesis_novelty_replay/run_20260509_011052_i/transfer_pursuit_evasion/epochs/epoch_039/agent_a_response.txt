def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(map(tuple, observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    self_role = (observation.get("self_role") or "").lower()
    pursuer = ("pursuer" in self_role) and ("evader" not in self_role)

    def cheb(x1, y1, x2, y2):
        ax = x1 - x2
        if ax < 0:
            ax = -ax
        ay = y1 - y2
        if ay < 0:
            ay = -ay
        return ax if ax > ay else ay

    def valid(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    best_move = [0, 0]
    best_val = -10**18 if pursuer else -10**18
    # For pursuer: maximize (-dist_to_opponent) and slight tie-break toward nearest resource.
    # For evader: maximize dist_to_opponent and also bias away from resources (or just ignore if none).
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d_op = cheb(nx, ny, ox, oy)

        if resources:
            d_res = min(cheb(nx, ny, rx, ry) for rx, ry in resources)
            if pursuer:
                val = (-d_op) * 1000 + (-d_res)
            else:
                val = (d_op) * 1000 + (-d_res)
        else:
            val = (-d_op) if pursuer else (d_op)

        if (pursuer and val > best_val) or ((not pursuer) and val > best_val):
            best_val = val
            best_move = [dx, dy]

    return best_move if valid(sx + best_move[0], sy + best_move[1]) else [0, 0]