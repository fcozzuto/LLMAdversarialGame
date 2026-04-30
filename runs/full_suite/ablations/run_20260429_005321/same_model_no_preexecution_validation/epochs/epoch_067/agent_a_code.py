def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles") or []
    resources = observation.get("resources") or []
    obs = {(int(x), int(y)) for x, y in obstacles}
    res = [(int(x), int(y)) for x, y in resources]

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def cheb(x1, y1, x2, y2):
        dx = x1 - x2; dx = dx if dx >= 0 else -dx
        dy = y1 - y2; dy = dy if dy >= 0 else -dy
        return dx if dx > dy else dy

    def free(x, y): return inb(x, y) and (x, y) not in obs

    cand = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            cand.append((dx, dy, nx, ny))
    if not cand:
        return [0, 0]

    best = (0, 0, 0, -10**18)
    for dx, dy, nx, ny in cand:
        if res:
            best_reach = 10**9
            opp_best = 10**9
            win_bonus = 0
            for rx, ry in res:
                myd = cheb(nx, ny, rx, ry)
                opd = cheb(ox, oy, rx, ry)
                if myd < best_reach: best_reach = myd
                if opd < opp_best: opp_best = opd
                if myd <= opd: win_bonus += 1
            score = 2.2 * win_bonus - 1.1 * best_reach
            # Pressure: move to make opponent's nearest resource harder
            score += 0.35 * (cheb(nx, ny, ox, oy) - cheb(sx, sy, ox, oy))
            # Slight preference to reduce separation to resources' vicinity without chasing opponent directly
            score += 0.08 * (-(cheb(nx, ny, ox, oy)))
        else:
            # No known resources: stabilize near opponent's corner by not allowing direct access
            score = -cheb(nx, ny, ox, oy)

        # Avoid moving adjacent to obstacles too much (keeps path flexibility)
        adj_obs = 0
        for adx, ady in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
            ax, ay = nx + adx, ny + ady
            if inb(ax, ay) and (ax, ay) in obs:
                adj_obs += 1
        score -= 0.15 * adj_obs

        if score > best[3]:
            best = (dx, dy, nx, score)

    return [int(best[0]), int(best[1])]