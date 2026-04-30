def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0):
            return dist
        dist[x0][y0] = 0
        qx, qy = [x0], [y0]
        i = 0
        while i < len(qx):
            x, y = qx[i], qy[i]
            i += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    distS = bfs(sx, sy)
    distO = bfs(ox, oy)

    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in resources:
        ds = distS[rx][ry]
        do = distO[rx][ry]
        if ds >= INF:  # unreachable for us
            continue
        # Prefer resources we can reach sooner than opponent; otherwise choose nearest feasible.
        key = (do - ds, -ds) if do < INF else (-ds, 0)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        # Fallback: move toward any reachable cell with minimal ds
        tx, ty = sx, sy
        best_ds = INF
        for rx, ry in resources:
            ds = distS[rx][ry]
            if ds < best_ds:
                best_ds = ds; tx, ty = rx, ry
        best = (tx, ty)

    tx, ty = best
    best_move = (0, 0)
    best_ds2 = distS[sx][sy]
    best_do2 = distO[sx][sy]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds2 = distS[nx][ny]
        do2 = distO[nx][ny]
        # If contested, try to increase the lead (do-ds); otherwise just minimize ds.
        if distO[tx][ty] < INF:
            score = do2 - ds2
            lead_key = (score, -ds2)
            if best_move == (0, 0) or lead_key > best_key:
                pass
        # Use deterministic selection:
        # Primary: minimize ds2 to target; Secondary: maximize (do2-ds2) as tie-break.
        key = (-ds2, do2 - ds2)
        cur_key = (-best_ds2, best_do2 - best_ds2)
        if best_move == (0, 0) or key > cur_key:
            best_move = (dx, dy)
            best_ds2 = ds2
            best_do2 = do2

    return [int(best_move[0]), int(best_move[1])]