def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    if not resources:
        return [0, 0]

    obst = {(x, y) for x, y in obstacles}

    def cheb(x1, y1, x2, y2):
        dx = x2 - x1
        if dx < 0:
            dx = -dx
        dy = y2 - y1
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    def clamp(v, lo, hi):
        return lo if v < lo else hi if v > hi else v

    best_move = [0, 0]
    best_val = -10**18

    # Deterministic candidate order to break ties
    for dx, dy in [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obst:
            continue

        # Evaluate action by best swing over resources
        val = 0.0
        # prefer immediate pickup and resource denial
        for i, (rx, ry) in enumerate(sorted(resources, key=lambda p: (p[0] * 8 + p[1], p[0], p[1]))):
            ds = cheb(nx, ny, rx, ry)
            do = cheb(ox, oy, rx, ry)
            cap = 4.0 if (nx, ny) == (rx, ry) else 0.0
            denial = 2.2 * (do - ds)
            dist_prefer = -0.12 * ds
            opp_pressure = 0.06 * (cheb(nx, ny, ox, oy))
            v = cap + denial + dist_prefer + opp_pressure + (-1e-6 * i)
            if v > val:
                val = v

        # Small bias toward staying within bounds center-ish to reduce dithering
        center_bias = -0.01 * (abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2))
        val += center_bias

        if val > best_val:
            best_val = val
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]