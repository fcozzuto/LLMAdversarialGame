def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def bfs_dist(start, limit=64):
        x0, y0 = start
        if not inb(x0, y0) or (x0, y0) in obstacles: return None
        INF = 10**9
        dist = [[INF]*w for _ in range(h)]
        dist[y0][x0] = 0
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            d = dist[y][x]
            if d >= limit: continue
            nd = d + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    q.append((nx, ny))
        return dist
    myd = bfs_dist((sx, sy))
    opd = bfs_dist((ox, oy))
    if myd is None or opd is None or not resources:
        tx, ty = (3, 3) if (sx <= 3) else (4, 4)
        best = (0, 0, 10**9, 10**9)  # dx,dy, new_d, new_opd
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                d = abs(nx - tx) + abs(ny - ty)
                o = abs(nx - ox) + abs(ny - oy)
                if (d, -o) < (best[2], -best[3]):
                    best = (dx, dy, d, o)
        return [best[0], best[1]] if (best[0] or best[1]) else [0, 0]
    INF = 10**9
    best_res = None
    best_score = -10**18
    for rx, ry in resources:
        dm = myd[ry][rx]; do = opd[ry][rx]
        if dm >= INF or do >= INF: 
            continue
        score = (do - dm) * 10 - dm  # prioritize winning contest then closeness
        if score > best_score or (score == best_score and (dm < myd[best_res[1]][best_res[0]] if best_res else True)):
            best_score = score
            best_res = (rx, ry)
    if best