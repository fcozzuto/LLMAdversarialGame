def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = observation.get("grid_width", 0)
    h = observation.get("grid_height", 0)
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set()
    for p in obs_list:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obstacles.add((p[0], p[1]))

    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            rx, ry = p[0], p[1]
            if (rx, ry) not in obstacles:
                res.append((rx, ry))
    if not res or w <= 0 or h <= 0:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def man(a, b, c, d):
        return abs(a - c) + abs(b - d)

    def legal(x, y, dx, dy):
        nx, ny = x + dx, y + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            return None
        if (nx, ny) in obstacles:
            return None
        return nx, ny

    def nearest_dist(x, y):
        bestd = None
        for rx, ry in res:
            d = man(x, y, rx, ry)
            if bestd is None or d < bestd:
                bestd = d
        return bestd if bestd is not None else 10**9

    best = None
    for dx, dy in moves:
        ns = legal(sx, sy, dx, dy)
        if ns is None:
            continue
        no = None
        bd = nearest_dist(ns[0], ns[1])
        # Opponent responds by trying to reduce its own nearest-resource distance.
        bestdo = None
        for odx, ody in moves:
            tmp = legal(ox, oy, odx, ody)
            if tmp is None:
                continue
            d = nearest_dist(tmp[0], tmp[1])
            if bestdo is None or d < bestdo:
                bestdo = d
                no = tmp
        if bestdo is None:
            bestdo = nearest_dist(ox, oy)
        score = (bd - bestdo, bd, -bestdo, dx, dy)
        if best is None or score < best[0]:
            best = (score, [dx, dy])

    return best[1] if best is not None else [0, 0]