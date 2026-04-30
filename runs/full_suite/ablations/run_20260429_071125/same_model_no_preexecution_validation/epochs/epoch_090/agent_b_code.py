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
        if not valid(x0, y0): return dist
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

    best = None
    best_key = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if dS[rx][ry] >= INF or dO[rx][ry] >= INF:
            continue
        # Maximize our advantage; break ties by earlier arrival to resource.
        key = (dO[rx][ry] - dS[rx][ry], -dS[rx][ry], dO[rx][ry])
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        # Fallback: move toward center-ish while avoiding obstacles.
        tx, ty = w // 2, h // 2
        dT = bfs(tx, ty)
        cx, cy = sx, sy
        bestm = (0, 0)
        bestv = dT[cx][cy]
        for dx, dy in moves:
            nx, ny = cx + dx, cy + dy
            if not valid(nx, ny): 
                continue
            v = dT[nx][ny]
            if v < bestv:
                bestv = v
                bestm = (dx, dy)
        return [int(bestm[0]), int(bestm[1])]

    rx, ry = best
    dR = bfs(rx, ry)  # distance from any cell to the chosen resource

    cx, cy = sx, sy
    bestm = (0, 0)
    cur_ds = dS[cx][cy]
    cur_do = dO[cx][cy]
    best_score = None
    for dx, dy in moves:
        nx, ny = cx + dx, cy + dy
        if not valid(nx, ny):
            continue
        # Prefer reducing distance to resource; when tied, keep opponent farther relative to us.
        ds = dR[nx][ny]
        score = (-ds, dS[nx][ny], -(dO[nx][ny] - dS[nx][ny]))
        if best_score is None or score > best_score:
            best_score = score
            bestm = (dx, dy)

    return [int(bestm[0]), int(bestm[1])]