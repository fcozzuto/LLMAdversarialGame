def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
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

    if not resources:
        # deterministic drift toward center while avoiding obstacles
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (0, 0); bestv = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            v = -(abs(nx - cx) + abs(ny - cy))
            if v > bestv:
                bestv = v; best = [dx, dy]
        return best

    # pick resource maximizing margin (opp slower) then minimizing own distance
    best_res = None
    best_key = None
    for rx, ry in resources:
        ds = distS[rx][ry]
        if ds >= INF: 
            continue
        do = distO[rx][ry]
        if do >= INF:
            key = (10**6, -ds)  # guaranteed win for reach
        else:
            key = (do - ds, -ds)
        # tie-break deterministically by coordinate
        key2 = (key[0], key[1], -rx, -ry)
        if best_key is None or key2 > best_key:
            best_key = key2
            best_res = (rx, ry)

    if best_res is None:
        # fallback: move to neighbor with smallest reachable distance to any resource
        target = None
        td = INF
        for rx, ry in resources:
            ds = distS[rx][ry]
            if ds < td:
                td = ds; target = (rx, ry)
        if target is None:
            return [0, 0]
        trx, try_ = target
    else:
        trx, try_ = best_res

    # choose step that decreases own distance to chosen target; if blocked, improve margin
    cur_ds = distS[trx][try_]
    best = [0, 0]
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ns = distS[nx][ny]
        if best_res is not None:
            margin_next = (distO[trx][try_] - ns) if distO[trx][try_] < INF else 10**6
            score = (margin_next, -ns, -abs(nx - trx) - abs(ny - try_), -nx, -ny)
        else:
            score = (-ns, -abs(nx - trx) - abs(ny - try_), -nx, -ny)
        if score > best_score:
            best_score = score
            best = [dx, dy]

    return best