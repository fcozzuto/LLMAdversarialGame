def choose_move(observation):
    w = int(observation.get("grid_width", 8)); h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    obstacles = set(tuple(map(int, p)) for p in (observation.get("obstacles") or []))
    resources = [tuple(map(int, p)) for p in (observation.get("resources") or [])]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0): return dist
        dist[x0][y0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x = qx[qi]; y = qy[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    distS = bfs(sx, sy)
    distO = bfs(ox, oy) if resources else None

    # If no resources: go toward more open area (deterministic: prefer farthest from opponent)
    if not resources:
        best = (0, 0); bestv = -INF
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): continue
            d = distS[nx][ny]
            if d >= INF: continue
            oo = 0
            if valid(ox, oy):
                oo = max(0, (distO[ox][oy] if distO else 0))
            # simple score: maximize distance to opponent position (Chebyshev)
            v = (max(abs(nx - ox), abs(ny - oy)) * 10 - d)
            if v > bestv:
                bestv = v; best = (dx, dy)
        return [best[0], best[1]]

    # Choose target that maximizes reach advantage: (do - ds), tie-break by shorter ds and resource index
    best_step = (0, 0); best_score = -INF
    # Precompute target value
    target_vals = []
    for i, (tx, ty) in enumerate(resources):
        ds = distS[tx][ty]; do = distO[tx][ty]
        if ds >= INF or do >= INF: continue
        # primary: do - ds (prefer earlier than opponent), secondary: smaller ds
        target_vals.append(((do - ds, -ds, -i), (tx, ty)))
    if not target_vals:
        # fall back: step to any valid cell minimizing ds to "center"
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (0, 0); bestd = INF
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny) and distS[nx][ny] < bestd:
                bestd = distS[nx][ny]; best = (dx, dy)
        return [best[0], best[1]]

    target_vals.sort(reverse=True)
    # Consider first few best targets to adapt if close-blocked
    candidates = [t for _, t in target_vals[:3]]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny): continue
        if distS[nx][ny] >= INF: continue
        # Evaluate best candidate target from this step
        stepv = -INF
        for tx, ty in candidates:
            ds = distS[tx][ty] - distS[nx][ny]  # remaining after step (not necessarily shortest due to BFS dist subtraction, but monotonic enough)
            ds0 = distS[tx][ty]
            do = distO[tx][ty]
            if ds0 >= INF or do >= INF: continue
            v = (do - ds0) * 100 + (-ds0)
            # Prefer moving closer to target direction deterministically
            v += - (abs(nx -