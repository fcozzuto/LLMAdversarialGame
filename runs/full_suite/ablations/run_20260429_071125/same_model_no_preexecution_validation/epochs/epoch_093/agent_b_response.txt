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
        if not valid(x0, y0): 
            return dist
        dist[x0][y0] = 0
        qx, qy = [x0], [y0]
        qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    dS = bfs(sx, sy)
    dO = bfs(ox, oy)

    def best_target():
        best = None
        for tx, ty in resources:
            ds = dS[tx][ty]
            if ds >= INF: 
                continue
            do = dO[tx][ty]
            contested = 0
            if do < INF and ds <= do:
                contested = 1
            key = (0 if contested else 1, ds if contested else ds - (do if do < INF else INF), tx, ty)
            if best is None or key < best[0]:
                best = (key, tx, ty)
        if best is None:
            return None
        return best[1], best[2]

    tgt = best_target()
    if tgt is None:
        # Fallback: head toward opponent to reduce their access
        dx, dy = 0, 0
        best = None
        for mx, my in moves:
            nx, ny = sx + mx, sy + my
            if not valid(nx, ny): 
                continue
            val = (abs((nx - ox)) + abs((ny - oy)), nx, ny)
            if best is None or val < best[0]:
                best = (val, mx, my)
        return [best[1], best[2]]

    tx, ty = tgt
    if sx == tx and sy == ty:
        return [0, 0]

    dT = bfs(tx, ty)
    best_move = None
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not valid(nx, ny):
            continue
        # Prefer reducing distance to target; slight tie-break toward opponent contest
        dt = dT[nx][ny]
        if dt >= INF:
            continue
        nn_do = dO[nx][ny] if dO else INF
        val = (dt, 0 if nn_do < INF and dt <= dT[ox][oy] else 1, nx, ny)
        if best_move is None or val