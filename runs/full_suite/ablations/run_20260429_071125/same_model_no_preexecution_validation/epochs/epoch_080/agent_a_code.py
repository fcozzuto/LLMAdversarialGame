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
    best_u = -INF
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not valid(rx, ry):
            continue
        ds = dS[rx][ry]
        if ds >= INF:
            continue
        do = dO[rx][ry]
        u = (do - ds) * 2 - ds
        if u > best_u or (u == best_u and (best is None or (ds, -do) < (dS[best[0]][best[1]], -dO[best[0]][best[1]]))):
            best_u = u
            best = (rx, ry)

    if best is None:
        return [0, 0]

    tx, ty = best
    cur_ds = dS[sx][sy]
    cur_do = dO[sx][sy]
    best_m = (0, 0)
    best_v = -INF
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ns = dS[nx][ny]  # already distance in BFS
        # Prefer closer to target, and being relatively closer than opponent
        v = -abs(dS[nx][ty] - dS[sx][ty])  # keep consistent progress
        v += -dS[nx][ty] * 2
        v += (dO[nx][ty] - dS[nx][ty]) * 3
        if (dS[nx][ty] < cur_ds) or ((dS[nx][ty] == cur_ds) and (dO[nx][ty] > cur_do)):
            v += 5
        if v > best_v:
            best_v = v
            best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]