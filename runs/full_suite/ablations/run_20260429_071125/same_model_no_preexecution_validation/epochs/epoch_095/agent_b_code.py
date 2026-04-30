def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0): return dist
        dist[x0][y0] = 0
        qx, qy, qi = [x0], [y0], 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    dS = bfs(sx, sy)
    dO = bfs(ox, oy)

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (0, 0); bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): continue
            v = - (abs(nx - cx) + abs(ny - cy))
            if v > bestv: bestv, best = v, (dx, dy)
        return [int(best[0]), int(best[1])]

    # Choose resource where we have the best "lead" (closer than opponent), with tie-break by speed.
    best_r = None; bestv = -10**18
    for tx, ty in resources:
        ds = dS[tx][ty]; do = dO[tx][ty]
        if ds >= INF: continue
        v = (do - ds) * 20 - ds  # strong preference for advantage; then sooner
        if v > bestv:
            bestv = v; best_r = (tx, ty)

    if best_r is None:
        # Fallback: any valid move that reduces our distance to opponent's side roughly.
        tx, ty = w - 1, h - 1
    else:
        tx, ty = best_r

    best = (0, 0); bestv = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny): continue
        ns = dS[nx][ny]
        no = dO[nx][ny]  # opponent distance from the same next cell (approximate pressure)
        if ns >= INF: continue
        v = (dO[tx][ty] - ns) * 20 - ns + (no - dS[tx][ty]) * 2
        # If we can step onto the resource, prioritize heavily.
        if (nx, ny) == (tx, ty): v += 10**6
        if v > bestv:
            bestv = v; best = (dx, dy)

    return [int(best[0]), int(best[1])]