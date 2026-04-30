def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources") or []
    obstacles = set(tuple(map(int, p)) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

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

    def cell_key(x, y):
        # deterministic ordering preference: closer to center, then lexicographic
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        return (-(abs(x - cx) + abs(y - cy)), x, y)

    if not resources:
        # drift to center while avoiding obstacles
        tx, ty = int(round((w - 1) / 2.0)), int(round((h - 1) / 2.0))
        bestm = (0, 0)
        bestd = INF
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): continue
            d = abs(nx - tx) + abs(ny - ty)
            if d < bestd or (d == bestd and (dx, dy) < bestm):
                bestd, bestm = d, (dx, dy)
        return list(bestm)

    distS = bfs(sx, sy)
    distO = bfs(ox, oy)

    best = None
    bestScore = (-INF, INF, INF, 0, 0)
    for p in resources:
        tx, ty = int(p[0]), int(p[1])
        ds, do = distS[tx][ty], distO[tx][ty]
        if ds >= INF: 
            continue
        # prefer winning contest (do - ds), then nearer ds, then farther do, then cell order
        sc = do - ds
        cand = (sc, ds, -do, tx, ty)
        if cand > bestScore:
            bestScore, best = cand, (tx, ty)

    tx, ty = best
    distT = bfs(tx, ty)  # distance from each cell to the target

    bestm = (0, 0)
    bestv = (INF, -distO[sx][sy], 0)  # lower dist-to-target, higher opponent distance, then prefer stay only if tied
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny): continue
        dt = distT[nx][ny]
        # estimate opponent pressure at this target: if opponent is close, prefer slower approach (maximize do - dt)
        oppPress = distO[tx][ty]
        v = (dt, -oppPress,