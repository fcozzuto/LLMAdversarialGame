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

    dS = bfs(sx, sy)
    dO = bfs(ox, oy)

    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            ds = dS[rx][ry]
            if ds >= INF:
                continue
            do = dO[rx][ry]
            if do >= INF:
                do = 10**6
            # Prefer resources we reach earlier (larger margin), then closer.
            margin = do - ds
            key = (margin, -ds, -(rx + ry), rx, ry)
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best if best is not None else (sx, sy)
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    cur = dS[tx][ty]
    # If unreachable, escape toward any reachable resource or toward center.
    if cur >= INF:
        targets = resources[:] if resources else [( (w-1)//2, (h-1)//2 )]
        best = None
        best_key = None
        for rx, ry in targets:
            ds = dS[rx][ry]
            if ds >= INF:
                continue
            do = dO[rx][ry]
            if do >= INF:
                do = 10**6
            key = (do - ds, -ds, -(rx + ry), rx, ry)
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best if best is not None else (sx, sy)

    cx = sx
    cy = sy
    best_move = (0, 0)
    best_move_key = None
    for dx, dy in moves:
        nx, ny = cx + dx, cy + dy
        if not valid(nx, ny):
            continue
        nd = dS[nx][ny]
        # Choose move that reduces distance to target; break ties safely/deterministically.
        key = (-(abs(nx - tx) + abs(ny - ty)), -nd, -dx, -dy)
        if best_move_key is None or key > best_move_key:
            best_move_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]