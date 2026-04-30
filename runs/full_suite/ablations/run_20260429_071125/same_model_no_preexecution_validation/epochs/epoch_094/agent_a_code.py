def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0): return dist
        dist[x0][y0] = 0
        qx, qy, qi = [x0], [y0], 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    dS = bfs(sx, sy)
    dO = bfs(ox, oy)
    if resources and (sx, sy) in set(resources):
        return [0, 0]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best, bestv = (0, 0), -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): continue
            v = -((nx - tx) * (nx - tx) + (ny - ty) * (ny - ty))
            if v > bestv or (v == bestv and (dx, dy) < best):
                bestv, best = v, (dx, dy)
        return [best[0], best[1]]

    res_set = set(resources)
    best_move, best_val = (0, 0), -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny): continue
        if (nx, ny) in res_set:
            return [dx, dy]

        worst = -INF
        for tx, ty in resources:
            ds = dS[nx][ny] + (0 if (tx, ty) in res_set else 0)
            ds2 = bfs(nx, ny)[tx][ty] if ds >= 0 else INF  # small, but deterministic
            do = dO[tx][ty]
            if ds2 >= INF or do >= INF:
                continue
            adv = do - ds2  # higher means we can reach earlier
            worst = max(worst, adv)
        if worst == -INF:
            worst = - (abs(nx - ox) + abs(ny - oy)) * 0.01

        # small tie-breaker: move that reduces distance to best reachable resource
        nearest = INF
        for tx, ty in resources:
            if dS[nx][ny] >= INF: continue
            ds = bfs(nx, ny)[tx][ty]
            if ds < nearest: nearest = ds
        opp_near = INF
        for tx, ty in resources:
            if dO[tx][ty] < opp_near: opp_near = dO[tx][ty]
        val = worst * 10 + (-nearest) + (opp_near - nearest) * 0.001

        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val, best