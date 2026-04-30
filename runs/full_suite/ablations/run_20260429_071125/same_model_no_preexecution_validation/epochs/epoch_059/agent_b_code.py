def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        if not valid(x0, y0): return [[INF] * h for _ in range(w)]
        dist = [[INF] * h for _ in range(w)]
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

    if not resources:
        return [0, 0]

    distS = bfs(sx, sy)
    distO = bfs(ox, oy)

    best = None
    best_sc = -INF
    for tx, ty in resources:
        ds = distS[tx][ty]
        do = distO[tx][ty]
        if ds >= INF and do >= INF:
            continue
        # Prefer resources we can reach; then prefer those we reach earlier than opponent.
        sc = (do - ds) * 100 - ds
        if sc > best_sc:
            best_sc = sc
            best = (tx, ty)

    if best is None:
        return [0, 0]

    tx, ty = best
    distT = bfs(tx, ty)

    # One-step greedy towards target, breaking ties by increasing opponent's distance to our next cell.
    bestm = (0, 0)
    best_key = (-INF, INF)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy