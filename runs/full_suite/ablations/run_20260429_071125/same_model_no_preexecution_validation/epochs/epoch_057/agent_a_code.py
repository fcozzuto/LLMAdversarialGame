def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
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

    distS = bfs(sx, sy)
    distO = bfs(ox, oy)

    if resources:
        best = None
        for tx, ty in resources:
            ds, do = distS[tx][ty], distO[tx][ty]
            if ds >= INF:
                continue
            race = 0 if ds < do else 1
            key = (race, ds, -do, tx, ty)
            if best is None or key < best[0]:
                best = (key, (tx, ty))
        if best is None:
            tx, ty = resources[0]
        else:
            tx, ty = best[1]
        distT = bfs(tx, ty)

        best_move = (None, None)
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dt = distT[nx][ny]
            if dt >= INF:
                continue
            adv_key = distO[nx][ny] - distS[nx][ny]
            key = (dt, -adv_key, dx, dy)
            if best_key is None or key < best_key:
                best_key = key
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No resources: move toward opponent to deny while staying valid.
    best_move = (0,