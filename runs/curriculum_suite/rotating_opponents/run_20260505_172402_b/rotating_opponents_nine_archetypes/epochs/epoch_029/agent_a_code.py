def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]

    def abs_i(a): return a if a >= 0 else -a

    def cheb(ax, ay, bx, by):
        dx = bx - ax
        if dx < 0: dx = -dx
        dy = by - ay
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    obs = set()
    obstacles = observation.get("obstacles") or []
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obs.add((x, y))

    def is_free(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obs

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if is_free(nx, ny):
            legal.append((dx, dy))
    if not legal:
        return [0, 0]

    resources = observation.get("resources") or []
    res = []
    for p in resources:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obs:
                res.append((x, y))
    if len(res) > 20:
        res = res[:20]

    if res:
        best = None
        bestv = 10**9
        for dx, dy in legal:
            nx, ny = sx + dx, sy + dy
            v = 10**9
            for x, y in res:
                ds = cheb(nx, ny, x, y)
                do = cheb(ox, oy, x, y)
                cand = ds - do
                if cand < v:
                    v = cand
            if v < bestv:
                bestv = v
                best = (dx, dy)
        return [best[0], best[1]]

    cx, cy = w // 2, h // 2
    best = None
    bestv = 10**9
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        v = cheb(nx, ny, cx, cy)
        if v < bestv:
            bestv = v
            best = (dx, dy)
    return [best[0], best[1]]