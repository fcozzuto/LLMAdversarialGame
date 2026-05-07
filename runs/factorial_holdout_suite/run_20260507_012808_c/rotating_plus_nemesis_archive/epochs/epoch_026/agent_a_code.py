def choose_move(observation):
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))

    resources = observation.get("resources") or []
    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h:
                res.append((x, y))
    if not res:
        return [0, 0]

    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def cheb(ax, ay, bx, by):
        dx = ax - bx
        if dx < 0: dx = -dx
        dy = ay - by
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    best = (None, None)
    best_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if nx < 0 or nx >= w or ny < 0 or ny >= h:
            continue
        blocked = (nx, ny) in obs
        my_min = 10**9
        opp_min = 10**9
        # choose best target under the same tie-break idea
        for rx, ry in res:
            myd = cheb(nx, ny, rx, ry)
            opd = cheb(ox, oy, rx, ry)
            # prefer targets where we reduce our distance relative to opponent
            key = (opd - myd, -myd, -rx, -ry)
            if key > (0, -10**9, -10**9, -10**9):
                pass
            if myd < my_min:
                my_min = myd
            if opd < opp_min:
                opp_min = opd
        # primary: maximize (opponent-nearest-to-some-resource - our-nearest-after-move)
        # secondary: minimize our nearest distance; also avoid blocked moves strongly.
        key = (opp_min - my_min, -my_min, -nx, -ny)
        if blocked:
            key = (key[0] - 10000, key[1] - 10000, key[2], key[3])
        if best_key is None or key > best_key:
            best_key = key
            best = (dx, dy)

    return [int(best[0]), int(best[1])]