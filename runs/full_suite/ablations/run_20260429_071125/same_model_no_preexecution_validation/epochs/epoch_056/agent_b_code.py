def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0):
            return dist
        dist[x0][y0] = 0
        qx, qy = [x0], [y0]
        qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    distS = bfs(sx, sy)
    distO = bfs(ox, oy)

    # Choose best resource deterministically: maximize advantage in arrival time, then closest, then far from opponent.
    best = None
    best_key = None
    for tx, ty in resources:
        ds = distS[tx][ty]
        if ds >= INF: 
            continue
        do = distO[tx][ty]
        # do may be INF if unreachable; treat as big so we prefer them
        if do >= INF: do = INF // 2
        adv = do - ds  # positive if we arrive earlier
        key = (adv, -ds, -(abs(tx - ox) + abs(ty - oy)))
        if best_key is None or key > best_key:
            best_key = key
            best = (tx, ty)

    # If no reachable resources, head to cell that maximizes distance to opponent (and is reachable).
    if best is None:
        best_cell = (sx, sy); best_d = -INF
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            dO = distO[nx][ny]
            dS = distS[nx][ny]
            if dS >= INF:
                continue
            if dO >= INF:
                dO = INF // 2
            sc = dO  # farther from opponent is better
            if sc > best_d:
                best_d = sc; best_cell = (nx, ny)
        return [best_cell[0] - sx, best_cell[1] - sy]

    # Move one step along shortest path to chosen target.
    tx, ty = best
    curd = distS[sx][sy]
    best_step = (sx, sy); best_val = INF
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = distS[nx][ny]
        if nd >= INF:
            continue
        # Prefer reducing distance to target; tie-break by increasing distance to opponent.
        if nd <= curd and nd < best_val:
            best_val = nd; best_step = (nx, ny)
        elif nd == best_val:
            if distO[nx][ny] > distO[best_step[0]][best_step[1]]:
                best_step = (nx, ny)

    return [best_step[0] - sx, best_step[1] - sy]