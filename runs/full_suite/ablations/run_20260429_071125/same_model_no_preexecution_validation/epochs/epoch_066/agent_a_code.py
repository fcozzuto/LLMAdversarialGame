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
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0): return dist
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

    dS = bfs(sx, sy)
    dO = bfs(ox, oy)

    best = None
    for rx, ry in resources:
        ds = dS[rx][ry]
        if ds >= INF: 
            continue
        do = dO[rx][ry]
        # Prefer arriving earlier than opponent; if both reachable, maximize advantage.
        # advantage = do - ds (larger is better). If opponent unreachable, do stays INF => huge advantage.
        adv = (do - ds) if do < INF else 10**6
        key = (-(adv), ds)  # minimize negative advantage (i.e., maximize adv), then smaller ds
        if best is None or key < best[0]:
            best = (key, (rx, ry))

    if best is None:
        # No reachable resources: drift toward center while avoiding obstacles.
        tx, ty = (w - 1) // 2, (h - 1) // 2
        target = (tx, ty)
    else:
        target = best[1]

    dT = bfs(target[0], target[1])

    # Choose legal move that minimizes distance to target (break ties toward larger x then y for determinism)
    best_move = (0, 0, INF, -1, -1)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dt = dT[nx][ny]
        if dt >= INF:
            continue
        cand = (dt, -nx, -ny)
        if cand < (best_move[2], best_move[3], best_move[4]):