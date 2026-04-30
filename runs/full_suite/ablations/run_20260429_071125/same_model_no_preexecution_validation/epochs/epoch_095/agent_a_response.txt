def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
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
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    dS = bfs(sx, sy)
    dO = bfs(ox, oy)

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (INF, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                val = abs(nx - tx) + abs(ny - ty)
                if (val, dx, dy) < best:
                    best = (val, dx, dy)
        return [int(best[1]), int(best[2])]

    if (sx, sy) in resources:
        return [0, 0]

    # Pick resource that we can reach earlier than opponent; break ties deterministically.
    best_r = None
    best_key = (-10**18, -10**18, 10**18, 10**18)
    for (tx, ty) in resources:
        ds = dS[tx][ty]
        do = dO[tx][ty]
        if ds >= INF:
            continue
        # Key: prioritize closeness advantage, then our speed, then deterministic coordinate.
        adv = do - ds  # positive => we are closer
        key = (adv, -ds, tx, ty)
        if key > best_key:
            best_key = key
            best_r = (tx, ty)

    if best_r is None:
        return [0, 0]
    tx, ty = best_r

    # Move to neighbor that minimizes our distance to target; tie-break by closeness to opponent.
    curd = dS[sx][sy]
    best = (10**18, 10**18, 10**18, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = dS[nx][ny]
        if nd >= INF:
            continue
        opp = dO[nx][ny]
        step = abs(dx) + abs(dy)
        key = (nd, -opp, step, dx, dy)
        if key < best:
            best = (nd, -opp, step, dx, dy)

    return [int(best[3]), int(best[4])]