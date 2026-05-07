def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles_list = observation.get("obstacles", []) or []
    obstacles = set()
    for p in obstacles_list:
        if p is None:
            continue
        obstacles.add((int(p[0]), int(p[1])))

    def clamp(x, y):
        if x < 0: x = 0
        elif x >= w: x = w - 1
        if y < 0: y = 0
        elif y >= h: y = h - 1
        return x, y

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best_move = (0, 0)
    best_score = -10**9

    def best_margin(px, py):
        # Maximize (opp_arrival - self_arrival); tie-break prefer smaller self_arrival
        best = (-10**9, 10**9, None)
        for rx, ry in resources:
            s = cheb(px, py, rx, ry)
            o = cheb(ox, oy, rx, ry)
            margin = o - s
            if margin > best[0] or (margin == best[0] and s < best[1]):
                best = (margin, s, (rx, ry))
        return best

    for dx, dy in moves:
        nx, ny = clamp(sx + dx, sy + dy)
        if (nx, ny) in obstacles:
            # Likely engine keeps position; still evaluate as staying
            nx, ny = sx, sy
        margin, sdist, target = best_margin(nx, ny)
        # Small deterministic penalties to reduce boundary/obstacle hugging
        pen = 0
        if nx == 0 or nx == w - 1: pen += 0.05
        if ny == 0 or ny == h - 1: pen += 0.05
        if (nx, ny) in obstacles: pen += 1.0
        score = margin - pen - 0.001 * sdist
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]