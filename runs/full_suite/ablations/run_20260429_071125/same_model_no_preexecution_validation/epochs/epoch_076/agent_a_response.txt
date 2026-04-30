def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles
    INF = 10**9

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

    resources = observation.get("resources") or []
    best = None
    best_val = -10**18
    best_ds = INF

    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not valid(rx, ry):
            continue
        ds = dS[rx][ry]
        do = dO[rx][ry]
        if ds >= INF or do >= INF:
            continue
        val = (do - ds) * 1000 - ds  # prefer resources we can reach earlier than opponent
        if val > best_val or (val == best_val and ds < best_ds):
            best_val, best_ds, best = val, ds, (rx, ry)

    tx, ty = best if best is not None else (w // 2, h // 2)

    # Choose next step: valid move that minimizes distance to target; tie-break by improving advantage vs opponent.
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dns = dS[nx][ny]
        dno = dO[nx][ny]
        cand.append((dns, -(dno - dS[tx][ty]), dx, dy))
    if not cand:
        return [0, 0]
    cand.sort()
    return [int(cand[0][2]), int(cand[0][3])]