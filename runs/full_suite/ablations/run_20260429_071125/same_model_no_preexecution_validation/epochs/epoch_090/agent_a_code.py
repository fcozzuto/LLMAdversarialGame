def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources") or []
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
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
        qx = [x0]
        qy = [y0]
        qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx)
                    qy.append(ny)
        return dist

    dS = bfs(sx, sy)
    dO = bfs(ox, oy)

    if not resources:
        cx, cy = w // 2, h // 2
        best = (0, 0, 0, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            md = abs(nx - cx) + abs(ny - cy)
            key = (-md, -dx, -dy, nx, ny)
            if key > best:
                best = key
        return [int(best[3] - sx), int(best[4] - sy)]

    best_tx, best_ty = int(resources[0][0]), int(resources[0][1])
    best_score = -10**18
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        ds = dS[rx][ry]
        if ds >= INF:
            continue
        do = dO[rx][ry]
        if do >= INF:
            do = INF
        # Prefer resources we can reach not behind; otherwise prefer large opponent lead to contest.
        if do == INF:
            score = 10**6 - ds
        else:
            score = (do - ds) * 1000 - ds
        # Deterministic tie-break
        if score > best_score or (score == best_score and (ds, do, rx, ry) < (dS[best_tx][best_ty], dO[best_tx][best_ty], best_tx, best_ty)):
            best_score = score
            best_tx, best_ty = rx, ry

    cur_ds = dS[best_tx][best_ty]
    best_move = (0, 0)
    best_key = (-10**18, 0, 0, 0)  # (primary, -ds, -opp_adv, dxdy code)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nds = dS[nx][best_ty]
        # If already on target (rare), don't care; otherwise push toward it.
        if nds >= INF:
            continue
        # Opponent advantage at target if both go there; compare with move direction by using their distance from target only.
        do = dO[best_tx][best_ty]
        if do >= INF:
            do = 10**9
        my_adv = do - nds