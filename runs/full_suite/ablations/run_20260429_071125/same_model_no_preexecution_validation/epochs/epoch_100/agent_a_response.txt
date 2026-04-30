def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(start):
        dist = [[INF] * h for _ in range(w)]
        x0, y0 = start
        if not valid(x0, y0):
            return dist
        dist[x0][y0] = 0
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    dS = bfs((sx, sy))
    dO = bfs((ox, oy))

    if not resources:
        for dx, dy in [(0, 0), (1, 1), (1, 0), (0, 1), (-1, 0), (0, -1), (-1, -1), (1, -1), (-1, 1)]:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                return [dx, dy]
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in resources:
        ds = dS[rx][ry]
        if ds >= INF:
            continue
        do = dO[rx][ry]
        if do >= INF:
            do = ds + 1000
        # Prefer resources where we are significantly closer than opponent
        margin = do - ds
        key = (-margin, ds, rx, ry)  # deterministic
        if best is None or key < best_key:
            best, best_key = (rx, ry), key

    tx, ty = best
    if sx == tx and sy == ty:
        return [0, 0]

    curd = dS[tx][ty]
    best_move = [0, 0]
    best_val = curd
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = dS[nx][ny]
        # primary: reduce our distance to target; secondary: also avoid moving into worse opponent position for same target
        if nd < best_val:
            best_val = nd
            best_move = [dx, dy]
        elif nd == best_val:
            # tie-break deterministically by opponent distance to target
            ov = dO[nx][ny]  # not exact, but deterministic and mildly responsive
            curv = dO[sx][sy]
            if ov < curv or (dx, dy) < (best_move[0], best_move[1]):
                best_move = [dx, dy]

    return best_move