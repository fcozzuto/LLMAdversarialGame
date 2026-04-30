def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obs_list = observation.get("obstacles", []) or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def bfs(start):
        if not inside(start[0], start[1]):
            return None
        INF = 10**9
        dist = [[INF]*h for _ in range(w)]
        dist[start[0]][start[1]] = 0
        q = [tuple(start)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inside(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))
    if not resources or myd is None or opd is None:
        return [0, 0]

    INF = 10**9
    best = None
    best_key = None
    for rx, ry in resources:
        d1 = myd[rx][ry]
        d2 = opd[rx][ry]
        if d1 >= INF or d2 >= INF:
            continue
        # Key: win more by arriving earlier; also consider absolute arrival to reduce total lag.
        # Deterministic tie-breaker by coordinate.
        advantage = d2 - d1
        key = (-1 if advantage > 0 else (0 if advantage == 0 else 1), -advantage, d1, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]

    tx, ty = best
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inside(nx, ny):
            candidates.append((dx, dy, myd[nx][ny] if myd and myd[nx][ny] < INF else INF))
    if not candidates:
        return [0, 0]
    # Prefer step that reduces distance to target; if tied, reduce opponent distance and use deterministic coordinate tie-break.
    scored = []
    for dx, dy, md in candidates:
        nxo, ny o = None, None
    for dx, dy, md in candidates:
        nxx, nyy = sx + dx, sy + dy
        od = opd[nxx][nyy] if opd and opd[nxx][nyy] < INF else INF
        scored.append((md, -od, dx, dy))
    scored.sort()
    dx, dy = scored[0][2], scored[0][3]
    return [dx, dy]