def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        if not valid(x0, y0): return [[INF] * h for _ in range(w)]
        dist = [[INF] * h for _ in range(w)]
        dist[x0][y0] = 0
        qx, qy, qi = [x0], [y0], 0
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

    opp_dist = bfs(ox, oy)
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def score_from(x0, y0):
        best = -INF
        for rx, ry in resources:
            d1 = bfs(x0, y0)[rx][ry]
            d2 = opp_dist[rx][ry]
            if d1 >= INF: 
                continue
            # Prefer grabbing resources before opponent; slight center bias to break ties deterministically
            val = (d2 - d1) * 10 - 0.01 * (abs(rx - cx) + abs(ry - cy))
            if val > best: best = val
        return best if best > -INF/2 else -0.01 * (abs(x0 - cx) + abs(y0 - cy))

    best_move, best_val = [0, 0], -INF
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny): 
            nx, ny = sx, sy
        v = score_from(nx, ny)
        if v > best_val:
            best_val = v
            best_move = [dx, dy]
    return best_move