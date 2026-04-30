def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((int(p[0]), int(p[1])) for p in obs_list)

    moves = [(-1, -1), (-1, 0), (-1, 1),
             (0, -1), (0, 0), (0, 1),
             (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        INF = 10**9
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

    res = []
    for p in resources:
        x, y = int(p[0]), int(p[1])
        if valid(x, y):
            res.append((x, y))
    if not res:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (0, 0)
        bestd = 10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): continue
            d = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
            if d < bestd:
                bestd = d; best = (dx, dy)
        return [int(best[0]), int(best[1])]

    dOpp = bfs(ox, oy)
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny): continue
        dSelf = bfs(nx, ny)
        min_dself = 10**9
        score = 0
        for rx, ry in res:
            ds = dSelf[rx][ry]
            do = dOpp[rx][ry]
            if ds >= 10**8: 
                continue
            if ds < min_dself: min_dself = ds
            advantage = do - ds  # positive means we arrive first
            if advantage > 0:
                score += 10 + 2 * advantage - ds * 0.1
            else:
                score -= 1 + ds * 0.05
        if min_dself < 10**9:
            score += 5.0 / (1 + min_dself)
        if (score > best_score) or (score == best_score and (nx, ny) < (sx + best_move[0], sy + best_move[1])):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]