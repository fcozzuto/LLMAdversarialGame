def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(start):
        dist = [[INF] * h for _ in range(w)]
        x0, y0 = start
        if not valid(x0, y0): return dist
        dist[x0][y0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x = qx[qi]; y = qy[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    distS = bfs((sx, sy))
    distO = bfs((ox, oy))

    if not resources:
        best = (-INF, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): continue
            d = max(abs(nx - ox), abs(ny - oy))
            key = (d, -dx, -dy)
            if key > (best[0], -best[1], -best[2]): best = (d, dx, dy)
        return [best[1], best[2]]

    best_key = (-INF, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny): continue
        my_best = INF
        for rx, ry in resources:
            d = distS[nx][ny] if (rx == nx and ry == ny) else (distS[rx][ry] - distS[sx][sy] + distS[nx][ny])
            if d < my_best: my_best = d
        # compute candidate value by considering the best single resource from the next position
        cand = -INF
        for rx, ry in resources:
            ds = distS[nx][ny] if (nx == rx and ny == ry) else distS[rx][ry] + (distS[nx][ny] - distS[sx][sy])
            do = distO[rx][ry]
            if ds >= INF or do >= INF: continue
            margin = do - ds
            # prefer earlier arrival and large margin
            val = 1000 * margin - ds
            if val > cand: cand = val
        key = (cand, -dx, -dy)
        if key > (best_key[0], -best_key[1], -best_key[2]):
            best_key = (cand, dx, dy)

    return [best_key[1], best_key[2]]