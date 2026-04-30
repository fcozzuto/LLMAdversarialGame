def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obst = {(p[0], p[1]) for p in obstacles}
    resset = {(p[0], p[1]) for p in resources}

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not dirs:
        return [0, 0]

    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obst:
            legal.append((dx, dy, nx, ny))

    if not legal:
        return [0, 0]

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy, nx, ny in legal:
            d = cheb(nx, ny, cx, cy)
            key = (d, dx, dy)
            if best is None or key < best:
                best = key
        return [best[1], best[2]]

    def my_nearest_dist(x, y):
        md = None
        for rx, ry in resources:
            d = cheb(x, y, rx, ry)
            if md is None or d < md:
                md = d
        return md if md is not None else 0

    def opp_nearest_dist(x, y):
        md = None
        for rx, ry in resources:
            d = cheb(x, y, rx, ry)
            if md is None or d < md:
                md = d
        return md if md is not None else 0

    my_opp_dist = opp_nearest_dist(ox, oy)
    cx, cy = (w - 1) // 2, (h - 1) // 2

    best_score = None
    best_move = (0, 0)
    for dx, dy, nx, ny in legal:
        my_d = my_nearest_dist(nx, ny)
        opp_d = my_opp_dist  # static approx; opponent response unknown
        center_bias = cheb(nx, ny, cx, cy)
        score = (-my_d) + (10.0 if (nx, ny) in resset else 0.0) + (0.15 * opp_d) - (0.02 * center_bias)
        if best_score is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]