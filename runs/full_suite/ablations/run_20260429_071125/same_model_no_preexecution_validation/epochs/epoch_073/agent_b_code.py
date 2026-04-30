def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources") or []
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles
    INF = 10**9

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0): return dist
        dist[x0][y0] = 0
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    dS = bfs(sx, sy)
    dO = bfs(ox, oy)

    res = []
    for p in resources:
        x, y = int(p[0]), int(p[1])
        if valid(x, y):
            ds = dS[x][y]
            if ds < INF:
                res.append((x, y, ds, dO[x][y]))
    if not res:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (-(max(abs(sx - tx), abs(sy - ty))), 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): continue
            prog = -max(abs(nx - tx), abs(ny - ty))
            neigh = 0
            for ddx, ddy in moves:
                if valid(nx + ddx, ny + ddy): neigh += 1
            cand = (prog + 0.02 * neigh, nx, ny)
            if cand > best: best = cand
        return [int(best[1] - sx), int(best[2] - sy)]

    # Pick a contested resource: prioritize being closer than opponent
    res.sort(key=lambda t: (-(t[2] - t[3]), t[2], t[0], t[1]))
    # Evaluate top few to keep deterministic and fast
    best_target = None
    best_score = -10**18
    for x, y, ds, do in res[:6]:
        # If opponent can't reach, grab priority
        reach_bonus = 0
        if do >= INF: reach_bonus = 20
        score = (-ds) + 0.7 * (do - ds) + reach_bonus
        if score > best_score or (score == best_score and (x, y) < (best_target[0], best_target[1]) if best_target else True):
            best_score = score
            best_target = (x, y)

    tx, ty = best_target
    best = (-10**18, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny): continue
        ds_next = dS[nx][ny]
        # progress toward target, avoid letting opponent get closer to same target
        prog = -max(abs(nx - tx),