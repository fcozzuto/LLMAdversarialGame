def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", [])
    obs_list = observation.get("obstacles", [])
    obstacles = set((p[0], p[1]) for p in obs_list)
    if not resources:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    # Pick resource we can contest: prefer those where we are <= opponent in Chebyshev.
    best_r = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        sd = cheb(sx, sy, rx, ry)
        od = cheb(ox, oy, rx, ry)
        # Key: prioritize contest/deny, then smaller own distance, then larger opponent distance.
        # Include a small bias toward staying closer to center.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_bias = int(abs(rx - cx) + abs(ry - cy))
        if sd <= od:
            key = (0, sd, -(od - sd), center_bias, rx, ry)
        else:
            key = (1, sd - od, od, center_bias, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry)
    rx, ry = best_r if best_r is not None else resources[0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best_m = (0, 0)
    best_k = None

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        sd2 = cheb(nx, ny, rx, ry)
        od2 = cheb(ox, oy, rx, ry)

        # Move choice: first ensure we keep/secure advantage over opponent.
        # Then minimize our distance, maximize opponent's distance, and prefer centrality.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center = abs(nx - cx) + abs(ny - cy)

        secure = 0 if sd2 <= od2 else 1
        key = (secure, sd2, -(od2 - sd2), center, dx, dy)
        if best_k is None or key < best_k:
            best_k = key
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]