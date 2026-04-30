def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = int(observation["grid_width"]), int(observation["grid_height"])
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def dist_cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    best_r = None
    best_score = None
    for rx, ry in resources:
        myd = dist_cheb(sx, sy, rx, ry)
        opd = dist_cheb(ox, oy, rx, ry)
        # Deterministic scoring:
        # 1) Prefer resources we can reach earlier (opd - myd positive).
        # 2) If racing isn't clearly in our favor, bias toward nearer resources.
        # 3) Add center preference to break ties.
        margin = opd - myd
        center_bias = -(abs(rx - (w - 1) / 2.0) + abs(ry - (h - 1) / 2.0))  # larger is better
        score = (margin, -myd, center_bias, -rx, -ry)
        if best_score is None or score > best_score:
            best_score = score
            best_r = (rx, ry)

    rx, ry = best_r
    moves = [(-1, -1), (0, -1), (1, -1),
             (-1, 0),  (0, 0),  (1, 0),
             (-1, 1),  (0, 1),  (1, 1)]

    # Evaluate next step locally, with obstacle penalty and target progress.
    best_move = [0, 0]
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        myd2 = dist_cheb(nx, ny, rx, ry)
        # Predict opponent race at same target using their direction-agnostic time (cheb from current).
        opd = dist_cheb(ox, oy, rx, ry)
        # Prefer decreasing distance; prioritize securing a lead margin if available.
        lead = opd - myd2
        progress = dist_cheb(sx, sy, rx, ry) - myd2
        key = (lead, progress, -myd2, -abs(nx - rx) - abs(ny - ry), -dx, -dy)
        if best_key is None or key > best_key:
            best_key = key
            best_move = [dx, dy]

    return best_move