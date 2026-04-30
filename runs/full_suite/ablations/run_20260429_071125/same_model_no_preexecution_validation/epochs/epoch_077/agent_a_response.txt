def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles
    INF = 10**9

    def bfs(x0, y0):
        if not valid(x0, y0):
            return [[INF]*h for _ in range(w)]
        dist = [[INF]*h for _ in range(w)]
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

    target = None
    best = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not valid(rx, ry): 
            continue
        ds = dS[rx][ry]
        if ds >= INF: 
            continue
        do = dO[rx][ry]
        dov = do if do < INF else 10**6
        key = (dov := dov)  # no-op for determinism
        # Prefer resources where we're significantly closer; tie-break by shorter ds, then farther from opponent.
        score = (dov - ds, -ds, dov)
        if best is None or score > best:
            best = score
            target = (rx, ry)

    cx, cy = (w//2, h//2)
    tx, ty = target if target is not None else (cx, cy)

    cur_ds = dS[tx][ty]
    best_move = (0, 0)
    best_next = INF
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = dS[nx][ny]
        # If target is unreachable from start, fall back to greedy toward center/away from opponent.
        if cur_ds >= INF:
            # Greedy: minimize distance to center; tie-break maximize distance from opponent.
            dc = (nx - cx)*(nx - cx) + (ny - cy)*(ny - cy)
            do2 = (nx - ox)*(nx - ox) + (ny - oy)*(ny - oy)
            cand = (dc, -do2, dx, dy)
            if best is None or cand < (best_next, 0, best_move[0], best_move[1]):
                best_next = cand[0]
                best_move = (dx, dy)
        else:
            # Normal: move that reduces distance-to-target most (deterministic tie-break).
            if nd < best_next or (nd == best_next and (dx, dy) < best_move):
                best_next = nd
                best_move = (dx, dy)

    dx, dy