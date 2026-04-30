def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation["self_position"])
    ox, oy = map(int, observation["opponent_position"])

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

    # If we are on invalid cell, just step to any valid neighbor deterministically.
    if distS[sx][sy] >= INF:
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    resources_sorted = sorted(resources, key=lambda p: (p[0], p[1]))
    best = None
    best_key = None

    for tx, ty in resources_sorted:
        ds = distS[tx][ty]
        if ds >= INF:
            continue
        do = distO[tx][ty]
        if do >= INF:
            do = INF
        # Prefer resources we can reach and where we beat opponent; if opponent unreachable, prioritize heavily.
        if do >= INF:
            key = (1, -ds)  # reachable, opponent can't: maximize advantage
        else:
            key = (0, (do - ds), -ds)  # maximize (do - ds), then faster
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)

    if best is None:
        # Fallback: move toward any reachable resource by greedy distS
        reachable = [(distS[x][y], x, y) for (x, y) in resources_sorted if distS[x][y] < INF]
        if not reachable:
            return [0, 0]
        reachable.sort()
        tx, ty = reachable[0][1], reachable[0][2]
    else:
        tx, ty = best

    best_move = (0, 0)
    best_next = INF

    # Choose next step that minimizes our BFS distance to target.
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = distS[nx][ny]
        if nd < best_next:
            best_next = nd
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]