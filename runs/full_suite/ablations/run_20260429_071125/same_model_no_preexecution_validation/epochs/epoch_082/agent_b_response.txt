def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources") or []
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
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

    # Evaluate each move by targeting a resource we are likely to reach first.
    best = None
    best_val = INF
    k = 0.6
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds0 = dS[nx][ny]
        if ds0 >= INF:
            continue
        # Find best target resource from this next cell
        val = INF
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            if not valid(rx, ry):
                continue
            ds = dS[nx][ny] + 0  # already at nx,ny
            ds = dS[rx][ry]
            do = dO[rx][ry]
            if ds >= INF:
                continue
            # Prefer resources where we are strictly better; otherwise penalize.
            closer_bonus = 0.0
            if do < INF and do <= ds:
                closer_bonus = (ds - do) + 4.0
            # Cost: our distance, opponent comparison, and urgency by total remaining resources.
            val_r = ds - k * (do if do < INF else ds) + closer_bonus
            if val_r < val:
                val = val_r
        if val == INF:
            # Fallback: drift toward nearest reachable resource area or toward center
            cx, cy = (w - 1) // 2, (h - 1) // 2
            val = abs(nx - cx) + abs(ny - cy) * 0.9
        # Deterministic tie-breaker: lexicographic move order by fixed iteration; keep smallest val.
        if val < best_val:
            best_val = val
            best = (dx, dy)

    if best is None:
        # If somehow all invalid, stay put
        return [0, 0]
    return [int(best[0]), int(best[1])]