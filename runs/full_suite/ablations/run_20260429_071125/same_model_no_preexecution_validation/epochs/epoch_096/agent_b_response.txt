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

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0):
            return dist
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

    if resources:
        best_r = None
        best_key = None
        for rx, ry in resources:
            ds = dS[rx][ry]
            if ds >= INF:
                continue
            do = dO[rx][ry]
            # Prefer resources we can reach sooner; also prefer ones opponent can't beat.
            key = (ds, -(do - ds), rx, ry)
            if best_key is None or key < best_key:
                best_key = key
                best_r = (rx, ry)
        tx, ty = best_r
    else:
        tx, ty = (w - 1) // 2, (h - 1) // 2

    cur_d = dS[tx][ty]
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds = dS[nx][ny]
        do = dO[tx][ty]
        # Score: decrease own distance; slight preference to increase opponent distance to target.
        score = (-ds, (do - ds), -abs((nx - ox)) - abs((ny - oy)), dx, dy)
        if score > best_score:
            best_score = score
            best_move = (dx, dy)

    if cur_d < INF and dS[sx + best_move[0]][sy + best_move[1]] > cur_d:
        # If all equal/blocked, fall back to a deterministic move toward target by greedy step.
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        if valid(sx + dx, sy + dy):
            return [dx, dy]
        if valid(sx + dx, sy):
            return [dx, 0]
        if valid(sx, sy + dy):
            return [0, dy]
        return [0, 0]

    return [int(best_move[0]), int(best_move[1])]