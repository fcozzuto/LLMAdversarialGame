def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources") or []
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0): return dist
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

    # Choose best resource: maximize (dO - dS), tie by smaller dS, then larger dO.
    best_t = None
    best_key = None
    for rx, ry in resources:
        rx, ry = int(rx), int(ry)
        ds = dS[rx][ry]
        do = dO[rx][ry]
        if ds >= INF or do >= INF:
            continue
        key = (do - ds, -ds, do)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    if best_t is None:
        # Fallback: head deterministically to reduce distance to center.
        tx, ty = (w - 1) / 2, (h - 1) / 2
        best = (0, 0)
        best_val = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): continue
            val = (abs(nx - tx) + abs(ny - ty), dx, dy)
            if best_val is None or val < best_val:
                best_val = val; best = (dx, dy)
        return [int(best[0]), int(best[1])]

    rx, ry = best_t
    # Choose move that improves our arrival time to target, and keeps advantage.
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny): continue
        ds2 = dS[nx][ny]
        adv2 = dO[rx][ry] - ds2
        score = (ds2, -adv2, abs((nx - rx)) + abs((ny - ry)), dx, dy)
        if best_score is None or score < best_score:
            best_score = score; best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]