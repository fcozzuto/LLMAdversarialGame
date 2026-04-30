def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    INF = 10**9

    def bfs(start):
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

    mydist = bfs((sx, sy))
    opdist = bfs((ox, oy))

    # Choose best target resource by lead potential; deterministic tie-break by position.
    if resources:
        best = None
        for rx, ry in resources:
            md = mydist[ry][rx]; od = opdist[ry][rx]
            if md >= INF: 
                continue
            lead = od - md  # want our distance smaller than opponent
            cand = (lead, -md, rx, ry)
            if best is None or cand > best[0]:
                best = (cand, (rx, ry))
        if best is None:
            resources = []
        else:
            tx, ty = best[1]
    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    # Evaluate moves: minimize my distance to target, and if tie maximize opponent being farther.
    bestm = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        md = mydist[ny][nx]
        od = opdist[ny][nx]
        score = (-md, od, -abs(nx - tx) - abs(ny - ty), dx, dy)  # deterministic
        if bestm is None or score > bestm[0]:
            bestm = (score, (dx, dy))

    if bestm is None:
        return [0, 0]
    return [int(bestm[1][0]), int(bestm[1][1])]