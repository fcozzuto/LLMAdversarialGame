def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    res = []
    for p in resources:
        if p and len(p) >= 2:
            res.append((p[0], p[1]))
    if not res:
        return [0, 0]

    obs = set()
    for p in obstacles:
        if p and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0:
            dx = -dx
        dy = y1 - y2
        if dy < 0:
            dy = -dy
        return dx if dx > dy else dy

    opp_best = 10**9
    for rx, ry in res:
        d = cheb(ox, oy, rx, ry)
        if d < opp_best:
            opp_best = d

    dirs = [(0, 0), (1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
    best_move = [0, 0]
    best_score = -10**30

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue

        my_best = 10**9
        my_second = 10**9
        for rx, ry in res:
            d = cheb(nx, ny, rx, ry)
            if d < my_best:
                my_second = my_best
                my_best = d
            elif d < my_second:
                my_second = d

        is_on_resource = 1 if (nx, ny) in set(res) else 0
        score = (opp_best - my_best) * 1000 + is_on_resource * 100000 - my_best - my_second * 0.01

        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move