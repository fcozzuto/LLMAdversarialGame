def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    if not resources:
        return [0, 0]

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

    best = None
    best_score = -10**18
    for tx, ty in resources:
        ds = distS[tx][ty]
        if ds >= INF:
            continue
        do = distO[tx][ty]
        if do >= INF:
            do = INF
        # Higher is better: prefer resources we can reach and beat opponent on.
        # Add tie-break to prefer nearer targets for quick pickup.
        beat = (do - ds) if do < INF else 1000
        score = beat * 100 - ds
        if score > best_score:
            best_score = score
            best = (tx, ty, ds, do)

    if best is None:
        return [0, 0]

    tx, ty, ds, do = best
    # Choose a move that reduces our distance to the chosen target, while not improving opponent too much.
    cur_best = -10**18
    chosen = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nds = distS[nx][ny]
        if nds >= INF:
            continue
        nod = distO[nx][ny]
        if nod >= INF:
            nod = INF
        # Primary: move closer to target; Secondary: keep lead vs opponent for that target.
        closer = (ds - nds)
        lead_next = (do - nod) if do < INF and nod < INF else (1000 if do < INF else 0)
        sc = closer * 1000 + lead_next * 10 - (nds // 2)
        if sc > cur_best:
            cur_best = sc
            chosen = (dx, dy)

    return [int(chosen[0]), int(chosen[1])]