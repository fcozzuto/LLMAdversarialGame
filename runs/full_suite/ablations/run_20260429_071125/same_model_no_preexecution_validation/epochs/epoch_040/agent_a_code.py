def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0):
            return dist
        dist[x0][y0] = 0
        qx = [x0]
        qy = [y0]
        qi = 0
        while qi < len(qx):
            x = qx[qi]
            y = qy[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx)
                    qy.append(ny)
        return dist

    if not resources:
        return [0, 0]
    if (sx, sy) in resources:
        return [0, 0]

    distS = bfs(sx, sy)
    distO = bfs(ox, oy)

    best = None
    best_val = -10**18
    for rx, ry in resources:
        ds = distS[rx][ry]
        do = distO[rx][ry]
        if ds >= INF:
            continue
        if do >= INF:
            val = 10**6 - ds
        else:
            val = (do - ds) * 100 - ds - max(0, ds - do) * 3
        if val > best_val or (val == best_val and (best is None or (ds < distS[best[0]][best[1]]))):
            best_val = val
            best = (rx, ry)

    if best is None:
        return [0, 0]

    tx, ty = best
    distT = bfs(tx, ty)

    best_move = (0, 0)
    best_step_val = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d