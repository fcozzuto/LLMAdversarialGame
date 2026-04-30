def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    INF = 10**9

    def bfs(start):
        x0, y0 = start
        dist = [[INF] * w for _ in range(h)]
        if not inb(x0, y0) or (x0, y0) in obstacles: return dist
        dist[y0][x0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x = qx[qi]; y = qy[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    mydist0 = bfs((sx, sy))
    odist = bfs((ox, oy))
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            candidates.append((dx, dy, nx, ny))
    if not candidates:
        return [0, 0]

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy, nx, ny in candidates:
            v = (abs(nx - cx) + abs(ny - cy), abs(nx - ox) + abs(ny - oy), dx, dy)
            if best is None or v < best[0]:
                best = (v, dx, dy)
        return [best[1], best[2]]

    def best_cost(dist_from):
        best = INF
        for rx, ry in resources:
            if (rx, ry) in obstacles: 
                continue
            a = dist_from[ry][rx]
            b = odist[ry][rx]
            if a >= INF//2: 
                continue
            val = a - 0.8 * (0 if b >= INF//2 else b)
            if val < best: best = val
        return best

    best_move = None
    for dx, dy, nx, ny in candidates:
        dnext = mydist0 if (nx, ny) == (sx, sy) else bfs((nx, ny))
        c = best_cost(dnext)
        # tie-break deterministically: prefer lower my dist to opponent, then dx,dy order
        t = dnext[oy][ox] if inb(ox, oy) else INF
        key = (c, t, dx, dy)
        if best_move is None or key < best_move[0]:
            best_move = (key, dx, dy)

    return [best