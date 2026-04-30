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
        qx, qy, qi = [x0], [y0], 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    dS = bfs(sx, sy)
    dO = bfs(ox, oy)

    if resources:
        # Consider candidate next cells and choose the one maximizing contest advantage.
        best_move = (0, 0)
        best_score = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            if dS[nx][ny] >= INF: 
                continue
            safety = -4.0 * (1 if dO[nx][ny] <= dS[nx][ny] else 0)  # discourage cells opponent can contest quickly

            local = -10**18
            for rx, ry in resources:
                rx, ry = int(rx), int(ry)
                ds_cur = dS[rx][ry]
                if ds_cur >= INF:
                    continue
                # Approximate remaining distance from candidate using shortest-path decomposition.
                ds_rem = ds_cur - dS[nx][ny]
                if ds_rem < 0:
                    continue
                do = dO[rx][ry]
                if do >= INF:
                    do = INF
                adv = float(do - (ds_rem + 0))  # positive means we likely arrive first
                # Strong preference for reachable/near resources.
                near = -0.2 * float(ds_rem)
                tie = -0.05 * abs((do - ds_rem) if do < INF else 20)
                val = adv *