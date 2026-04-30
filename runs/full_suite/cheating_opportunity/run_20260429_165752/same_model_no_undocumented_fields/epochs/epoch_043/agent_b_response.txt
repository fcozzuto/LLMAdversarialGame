def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [0, 0]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    cx, cy = w // 2, h // 2
    if not resources:
        best = None
        bestv = None
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            v = -(cheb(nx, ny, cx, cy)) - 0.05 * cheb(nx, ny, ox, oy)
            if best is None or v > bestv or (v == bestv and (dx, dy) < best):
                best, bestv = (dx, dy), v
        return [best[0], best[1]]

    best_move = None
    best_score = None
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        my_best = 10**9
        opp_best_gap = -10**9
        for rx, ry in resources:
            d_m = cheb(nx, ny, rx, ry)
            d_o = cheb(ox, oy, rx, ry)
            gap = d_o - d_m  # positive means we are closer (or opponent farther)
            if gap > opp_best_gap:
                opp_best_gap = gap
                my_best = d_m
            elif gap == opp_best_gap and d_m < my_best:
                my_best = d_m
        # tie-break: prefer approaching opponent's likely race lanes by reducing our distance and not getting too far from it
        score = opp_best_gap - 0.01 * my_best - 0.0001 * cheb(nx, ny, ox, oy)
        if best_move is None or score > best_score or (score == best_score and (dx, dy) < best_move):
            best_move, best_score = (dx, dy), score

    return [best_move[0], best_move[1]]