def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles
    INF = 10**9
    def bfs(start):
        sx0, sy0 = start
        dist = [[INF] * h for _ in range(w)]
        if not valid(sx0, sy0): return dist
        qx = [sx0]; qy = [sy0]; qi = 0
        dist[sx0][sy0] = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0: continue
                    nx, ny = x + dx, y + dy
                    if valid(nx, ny) and nd < dist[nx][ny]:
                        dist[nx][ny] = nd
                        qx.append(nx); qy.append(ny)
        return dist
    distS = bfs((sx, sy))
    distO = bfs((ox, oy))
    best_move = (0, 0)
    best_key = (-10**12, -10**12)  # (positive_margin, -time)
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        key = (-10**12, -10**12)
        for rx, ry in resources:
            ds = distS[nx][ny] if (nx == sx and ny == sy) else INF
            # To avoid per-move BFS, approximate ds by direct move on distS
            # (distS is exact from current self; after move, we adjust locally if possible)
            ds = INF
            for adx in (-1, 0, 1):
                for ady in (-1, 0, 1):
                    px, py = nx - adx, ny - ady
                    if 0 <= px < w and 0 <= py < h and distS[px][py] < INF and valid(nx, ny):
                        ds = min(ds, distS[px][py] + 1)
            do = distO[rx][ry]
            if ds >= INF or do >= INF:
                continue
            margin = do - ds
            # primary: maximize advantage, secondary: arrive sooner (smaller ds), tertiary: prioritize larger do
            k0 = margin
            k1 = -ds
            if (k0, k1) > key:
                key = (k0, k1)
        if key[0] > best_key[0] or (key[0] == best_key[0] and key[1] > best_key[1]):
            best_key = key
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]