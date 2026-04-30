def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)
    inb = lambda x, y: 0 <= x < w and 0 <= y < h
    blocked = lambda x, y: (not inb(x, y)) or ((x, y) in obs)
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    if not resources or blocked(sx, sy) or blocked(ox, oy):
        return [0, 0]
    res = [(r[0], r[1]) for r in resources]
    if (sx, sy) in set(res):
        return [0, 0]

    INF = 10**9
    def bfs(start):
        if blocked(start[0], start[1]): return None
        dist = [[INF] * w for _ in range(h)]
        x0, y0 = start
        dist[y0][x0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if not blocked(nx, ny) and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    mydist = bfs((sx, sy))
    opd = bfs((ox, oy))
    if mydist is None or opd is None:
        return [0, 0]

    def cheb(ax, ay, bx, by):
        dx = ax - bx; dx = -dx if dx < 0 else dx
        dy = ay - by; dy = -dy if dy < 0 else dy
        return dx if dx >= dy else dy

    # Opponent pressure target: resource where opponent is closest
    opp_best_d = INF; opp_best = None
    for rx, ry in res:
        d = opd[ry][rx]
        if d < opp_best_d:
            opp_best_d = d; opp_best = (rx, ry)

    def score_move(nx, ny):
        if blocked(nx, ny):
            return -10**12
        best = -10**12
        for rx, ry in res:
            dm = mydist[ny][nx] + 0  # local offset using next BFS dist for next pos not available
            # Approximate dm from next cell using Chebyshev to stay fast/deterministic:
            dm = min(mydist[ny][rx], cheb(nx, ny, rx) + 0)
            do = opd[ry][rx]
            if do >= INF or dm >= INF:
                continue
            # Primary: reach-first advantage; Secondary: closeness; Tertiary: avoid being easily trapped by opponent
            key = (do - dm, -dm, -(rx + ry))
            val = key[0] * 100 - key[1] + key[2]
            best = val if val > best else best
        # If we can't find any good resource, respond by separating from opponent while moving around