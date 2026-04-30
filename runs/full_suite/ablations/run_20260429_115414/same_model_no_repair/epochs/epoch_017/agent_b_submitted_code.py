def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def bfs(start):
        if not inside(start[0], start[1]):
            return None
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        x0, y0 = start
        dist[x0][y0] = 0
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inside(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))
    if myd is None:
        return [0, 0]
    if not resources:
        # move toward nearest corner that is not blocked by obstacles
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        best = None
        for cx, cy in corners:
            if inside(cx, cy):
                d = myd[cx][cy]
                if d < (best[0] if best else 10**9):
                    best = (d, cx, cy)
        tx, ty = (best[1], best[2]) if best else (sx, sy)
        beststep = [0, 0]
        bestd = myd[tx][ty]
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inside(nx, ny) and myd[nx][ny] < bestd:
                bestd = myd[nx][ny]
                beststep = [dx, dy]
        return beststep

    # Choose resource where we are relatively faster than opponent.
    chosen = None
    for rx, ry in resources:
        if inside(rx, ry):
            d1 = myd[rx][ry]
            d2 = opd[rx][ry] if (opd is not None) else 10**9
            if d1 < 10**9:
                # Prefer having smaller (d1 - d2). Tie-break deterministically.
                rel = d1 - d2
                parity = ((rx + ry) & 1)
                key = (rel, d1, -parity, rx, ry)
                if chosen is None or key < chosen[0]:
                    chosen = (key, (rx, ry))
    if chosen is None:
        return [0, 0]

    tx, ty = chosen[1]
    curd = myd[tx][ty]
    # Step that most reduces our distance to target; avoid steps that clearly worsen relative position.
    best = [0, 0]
    best_score = (10**9, 10**9, 0)  # (mydist, -opponentdist, dx, dy) simplified by tuple ordering
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        nd1 = myd[nx][ny]
        if nd1 >= curd:
            # still allow if stuck (all candidates equal/unreachable)
            pass
        nd2 = opd[nx][ny] if (opd is not None) else 10**9
        # Primary: smaller distance to target
        # Secondary: if close, prefer cells where opponent is not closer to target (using nd1-nd2 surrogate)
        score =