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

    dS = bfs(sx, sy)
    dO = bfs(ox, oy)

    best = None
    best_key = (-INF, INF)  # (advantage, self_dist)
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not valid(rx, ry): 
            continue
        ds, do = dS[rx][ry], dO[rx][ry]
        if ds >= INF: 
            continue
        adv = do - ds
        key = (adv, ds)
        if key[0] > best_key[0] or (key[0] == best_key[0] and key[1] < best_key[1]):
            best_key = key
            best = (rx, ry)

    cx, cy = sx, sy
    if best is None:
        best_move = (0, 0)
        best_val = (-INF, INF, 0)
        for dx, dy in moves:
            nx, ny = cx + dx, cy + dy
            if not valid(nx, ny): 
                continue
            ds = dS[nx][ny]
            do = dO[nx][ny]
            val = (do - ds, do, (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy))
            if val > best_val:
                best_val = val
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    rx, ry = best
    curr_ds = dS[rx][ry]
    best_move = (0, 0)
    best_val = (INF, -INF, INF)  # minimize ds_to_target, maximize opp_adv_after, tie by do_to_target
    for dx, dy in moves:
        nx, ny = cx + dx, cy + dy
        if not valid(nx, ny):
            continue
        ds2 = dS[nx][ny]
        # heuristic: move that reduces distance to target most; use opponent distance at new pos to break ties
        to_target_ds = bfs(nx, ny)[rx][ry] if False else dS[rx][ry]  # keep deterministic, constant
        # use precomputed distances from new pos to target via dS distances backward approximation:
        # (since diagonal BFS metric, use direct ds from new pos to target via BFS only if needed; avoid cost)
        # Better: choose by distance from new pos