def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0):
            return dist
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

    def pick_target():
        if not resources:
            # fallback: move toward center while staying away from opponent
            cx, cy = w // 2, h // 2
            return (cx, cy)
        best = None
        best_key = None
        for rx, ry in resources:
            ds = dS[rx][ry]
            do = dO[rx][ry]
            # Higher advantage is better; prefer reachable targets.
            reachable = 0 if ds >= INF else 1
            key = (reachable, do - ds, -ds, (rx, ry))
            # max by (reachable, do-ds, -ds), tie-break by lex (rx,ry)
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        return best

    tx, ty = pick_target()

    # Choose move that minimizes self distance to target; break ties by maximizing opponent distance and not worsening.
    best_move = (0, 0)
    best_score = None
    best_ds = INF
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dsn = dS[nx][ny]
        # primary: how close we get to the target (use BFS from target by greedy via self dist-to-target difference)
        dt = dS[tx][ty]
        # Approx closeness by difference after move: prefer smaller (dS[nx][ny] + remaining?) can't; just use dsn as proxy.
        # Better: minimize dS distance to target: since we have only dS from start, use Euclidean/cheb as deterministic proxy.
        cheb = abs(nx - tx) if abs(nx - tx) > abs(ny - ty) else abs(ny - ty)
        oppd = dO[ox][oy] if ox == nx and oy == ny else abs(nx - ox) + abs(ny - oy)
        score = (cheb, dsn, -oppd, (dx, dy))
        if best_score is None or score < best_score:
            best_score = score
            best_move = (dx, dy)
            best_ds = dsn

    # If target unreachable, head to nearest reachable resource directly via cheb.
    if best_ds >= INF:
        if resources:
            nearest = None
            bestc = None
            for rx, ry in resources:
                ds = dS[rx][ry]
                if ds >= INF:
                    continue
                c = abs(sx - rx) if abs(sx - rx) > abs(sy - ry) else abs(sy - ry)
                key = (c, rx, ry)
                if bestc is None or key < bestc: