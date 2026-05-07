def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles_in = observation.get("obstacles") or []
    obstacles = set()
    for p in obstacles_in:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = p[0], p[1]
            if isinstance(x, int) and isinstance(y, int) and 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    deltas = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    legal = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            legal.append((dx, dy, nx, ny))
    if not legal or not resources:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    obs_adj = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]

    def dist(x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def prox_pen(x, y):
        pen = 0
        for ax, ay in obs_adj:
            if (x + ax, y + ay) in obstacles:
                pen += 1
        return pen

    best_move = (0, 0, sx, sy)
    best_score = None
    for dx, dy, nx, ny in legal:
        center_pen = (abs(nx - cx) + abs(ny - cy)) * 0.02
        my_prox = prox_pen(nx, ny) * 0.3
        # Choose the best resource outcome assuming we go for that resource next.
        best_res_score = None
        for rx, ry in resources:
            ds = dist(nx, ny, rx, ry)
            do = dist(ox, oy, rx, ry)
            slack = do - ds  # positive: we are closer to this resource
            # Prefer resources where we can win (slack high), otherwise still reduce our distance.
            s = ds - 1.6 * slack + center_pen * 0.5 + my_prox + (abs(rx - ox) + abs(ry - oy)) * 0.001
            if best_res_score is None or s < best_res_score:
                best_res_score = s
        if best_score is None or best_res_score < best_score:
            best_score = best_res_score
            best_move = (dx, dy, nx, ny)

    return [best_move[0], best_move[1]]