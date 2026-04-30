def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    INF = 10**9

    def bfs(start):
        dist = [[INF] * h for _ in range(w)]
        x0, y0 = start
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

    ds = bfs((sx, sy))
    do = bfs((ox, oy))

    if not resources:
        best = (0, 0)
        bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): continue
            dfo = abs(nx - ox) + abs(ny - oy)
            if dfo > bestv:
                bestv = dfo
                best = (dx, dy)
        return [best[0], best[1]]

    best_score = -10**18
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny): continue
        safety = abs(nx - ox) + abs(ny - oy)
        # prefer resources we can reach earlier than opponent
        target_best = -10**18
        for rx, ry in resources:
            d1 = ds[rx][ry]
            d2 = do[rx][ry]
            if d1 >= INF: continue
            # smaller is better; include tie-breaking toward safety
            advantage = (d2 - d1)  # positive means we are earlier
            # add slight incentive for being closer right now
            dcur = ds[nx][ny]  # always 0 for start, but keep deterministic
            score = 5.0 * advantage - 0.1 * d1 + 0.001 * dcur + 0.03 * safety
            if score > target_best:
                target_best = score
        if target_best > best_score:
            best_score = target_best
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]