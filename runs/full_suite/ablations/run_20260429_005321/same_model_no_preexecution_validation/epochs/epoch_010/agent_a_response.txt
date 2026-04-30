def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def bfs(start):
        INF = 10**9
        x0, y0 = start
        dist = [[INF] * w for _ in range(h)]
        if not inb(x0, y0) or (x0, y0) in obstacles:
            return dist
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
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (10**9, None)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles: 
                continue
            score = abs(nx - cx) + abs(ny - cy) + abs(nx - ox) + abs(ny - oy) * 0.01
            if score < best[0]: best = (score, (dx, dy))
        return list(best[1]) if best[1] is not None else [0, 0]

    our_dist = bfs((sx, sy))
    opp_dist = bfs((ox, oy))

    best_score = -10**18
    best_res = None
    for rx, ry in resources:
        od = our_dist[ry][rx]
        pd = opp_dist[ry][rx]
        if od >= 10**9: 
            continue
        if pd >= 10**9:
            pd = 10**6
        score = (pd - od) * 1000 - od - (rx + ry * 0.001)
        if score > best_score:
            best_score = score
            best_res = (rx, ry, od)
    if best_res is None:
        return [0, 0]

    tx, ty, td = best_res
    best_move = [0, 0]
    best_tie = (10**9, 10**9)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nd = our_dist[ny][nx]
        if nd < 10**9 and nd <= td:
            # Prefer strict progress; tie-break by staying farther from opponent.
            progress = td - nd
            oppd = abs(nx - ox) + abs(ny - oy)
            tie = (-progress, -oppd)
            if tie < best_tie:
                best_tie = tie
                best_move = [dx, dy]
    return best_move