def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources") or []
    obstacles = set(tuple(map(int, p)) for p in (observation.get("obstacles") or []))
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

    best = None
    best_val = -10**18
    for p in resources:
        rx, ry = int(p[0]), int(p[1])
        ds = dS[rx][ry]
        if ds >= INF:
            continue
        do = dO[rx][ry]
        if do >= INF:
            do = INF
        # Prefer resources we reach first; otherwise choose ones with a strong advantage in distance.
        if do == INF:
            val = 1000000 - ds
        else:
            gap = do - ds
            val = gap * 1000 - ds
        if val > best_val:
            best_val = val
            best = (rx, ry, ds)

    # If no reachable resource: head to the nearest reachable cell toward opponent's direction (deterministic).
    if best is None:
        # Prefer moving to reduce Manhattan distance to (ox, oy) while staying valid.
        cx, cy = ox, oy
        best_move = (0, 0)
        best_md = INF
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            md = abs(nx - cx) + abs(ny - cy)
            if md < best_md:
                best_md = md
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    tx, ty = best[0], best[1]
    # Choose next step that strictly improves distance-to-target if possible, else stay still.
    curd = dS[sx][sy]
    best_move = (0, 0)
    best_dist = curd
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = dS[nx][ny]  # distance-from-self BFS grid already computed, not from target
        # Instead, use approximate: prefer move that minimizes shortest path length to target by local BFS dist from target not available.
        # We'll use dist-to-target via bfs from target at most once (still deterministic).
    dT = bfs(tx, ty)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = dT[nx][ny]
        if nd < best_dist:
            best_dist = nd
            best_move = (dx, dy)

    # Ensure we never return an invalid move (engine would keep us, but avoid repeats).
    nx, ny = sx + best_move[0], sy + best_move[1]
    if not valid(nx, ny):
        return [0, 0]
    return [best_move[0], best_move[1]]