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

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    def free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

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

    if not resources:
        best = None
        bestv = -10**18
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            v = -cheb(nx, ny, ox, oy)
            if v > bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    best_overall = None
    best_val = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        # Value a move by the best resource we can reach sooner than the opponent.
        best_res = -10**18
        nearest = 10**9
        for rx, ry in resources:
            sd = cheb(nx, ny, rx, ry)
            od = cheb(ox, oy, rx, ry)
            # Higher is better: (opponent distance - our distance)
            v = (od - sd) * 1000 - sd * 2
            if v > best_res:
                best_res = v
            nd = cheb(nx, ny, rx, ry)
            if nd < nearest:
                nearest = nd
        # Also slightly prefer staying away from opponent to avoid giving them contested positions.
        opp_pen = cheb(nx, ny, ox, oy) * 3
        total = best_res - opp_pen - nearest
        if total > best_val:
            best_val = total
            best_overall = (dx, dy)

    return [int(best_overall[0]), int(best_overall[1])]