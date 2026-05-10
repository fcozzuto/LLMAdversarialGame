def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    self_role = observation.get("self_role", "pursuer")
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def bfs_from(start):
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        dist[start[0]][start[1]] = 0
        qx, qy = [start[0]], [start[1]]
        qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if not inb(nx, ny):
                    continue
                if dist[nx][ny] > nd:
                    dist[nx][ny] = nd
                    qx.append(nx)
                    qy.append(ny)
        return dist

    if self_role == "pursuer":
        dist = bfs_from((ox, oy))
        best = None
        bestd = 10**9
        bestdx = 0
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = dist[nx][ny]
            if d < bestd or (d == bestd and (abs(nx - ox) + abs(ny - oy), abs(nx - (w - 1)) + abs(ny - (h - 1))) < best):
                best = (abs(nx - ox) + abs(ny - oy), abs(nx - (w - 1)) + abs(ny - (h - 1)))
                bestd = d
                bestdx = dx
                bestdy = dy
        return [bestdx, bestdy] if best is not None else [0, 0]
    else:
        # evader: move to maximize shortest-path distance from pursuer
        dist = bfs_from((ox, oy))
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        target = max(corners, key=lambda p: abs(p[0] - sx) + abs(p[1] - sy))
        bestd = -1
        bestscore = -1
        bestdx = bestdy = 0
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny):
                continue
            d = dist[nx][ny]
            corner_bias = abs(target[0] - nx) + abs(target[1] - ny)
            score = (d, corner_bias)
            if score > (bestd, bestscore):
                bestd, bestscore = d, corner_bias
                bestdx, bestdy = dx, dy
        return [bestdx, bestdy]