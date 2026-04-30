def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0):
            return dist
        dist[x0][y0] = 0
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    distS = bfs(sx, sy)
    distO = bfs(ox, oy)

    if not resources:
        bestm, bestd = (0, 0), distS[sx][sy]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                d = distS[nx][ny]
                if d < bestd or (d == bestd and (dx, dy) < bestm):
                    bestd, bestm = d, (dx, dy)
        return [bestm[0], bestm[1]]

    best_t = None
    best_val = -10**18
    for tx, ty in resources:
        ds = distS[tx][ty]
        if ds >= INF:
            continue
        do = distO[tx][ty]
        if do >= INF:
            val = 10**6 - ds
        else:
            # Prefer winning the race; then closest; then further from opponent.
            val = 2000 * (do - ds) + (1 if ds <= do else -1) * 500 - ds
        if val > best_val or (val == best_val and (ds, -do, tx, ty) < (distS[best_t[0]][best_t[1]], -distO[best_t[0]][best_t[1]], best_t[0], best_t[1])):
            best_val = val
            best_t = (tx, ty)

    if best_t is None:
        # Move toward nearest reachable resource.
        bestm, bestd = (0, 0), INF
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                d = distS[nx][ny]
                if d < bestd or (d == bestd and (dx, dy) < bestm):
                    bestd, bestm = d, (dx, dy)
        return [bestm[0], bestm[1]]

    tx