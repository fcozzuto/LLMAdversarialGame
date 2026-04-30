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
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
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
        best_val = -10**9
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            val = cheb(nx, ny, ox, oy)
            if val > best_val:
                best_val = val
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    # New policy: contest resources by moving to where we reduce our time-to-closest
    # while increasing opponent's time-to-closest; also keep distance from opponent.
    best = legal[0]
    best_val = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        our_min = 10**9
        opp_min = 10**9
        for rx, ry in resources:
            d1 = cheb(nx, ny, rx, ry)
            if d1 < our_min:
                our_min = d1
            d2 = cheb(ox, oy, rx, ry)
            if d2 < opp_min:
                opp_min = d2
        dist_opp = cheb(nx, ny, ox, oy)
        val = (opp_min - our_min) * 10 + dist_opp
        if val > best_val:
            best_val = val
            best = (dx, dy)

    return [int(best[0]), int(best[1])]