def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return not inb(x, y) or (x, y) in obstacles

    if (sx, sy) in resources or not resources:
        return [0, 0]

    INF = 10**9
    def bfs(start):
        x0, y0 = start
        if blocked(x0, y0): return None
        dist = [[INF] * w for _ in range(h)]
        dist[y0][x0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if not blocked(nx, ny) and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    myd = bfs((sx, sy)); opd = bfs((ox, oy))
    if myd is None or opd is None:
        return [0, 0]

    best_t = None
    best_score = -INF
    for rx, ry in resources:
        d1 = myd[ry][rx]; d2 = opd[ry][rx]
        if d1 >= INF or d2 >= INF: 
            continue
        # Prefer resources we can reach earlier; otherwise contest strongly
        lead = d2 - d1
        score = lead * 10 - d1
        if score > best_score:
            best_score = score
            best_t = (rx, ry)

    if best_t is None:
        # Try to move toward opponent's nearest reachable resource (to disrupt)
        nearest = None; nearest_d = INF
        for rx, ry in resources:
            d2 = opd[ry][rx]
            if d2 < nearest_d and d2 < INF:
                nearest_d = d2; nearest = (rx, ry)
        best_t = nearest
        if best_t is None:
            return [0, 0]

    rx, ry = best_t
    if myd[ry][rx] >= INF:
        return [0, 0]

    curd = myd[sy][sx]
    best_move = (0, 0); best_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny): 
            continue
        if myd[ny][nx] >= myd[sy][sx]:  # don't go uphill in shortest path to target
            continue
        d_op = opd[ny][nx]
        # Tie-break toward moves that reduce distance to our target and also keep away from opponent
        key = (myd[ny][nx], -d_op, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]