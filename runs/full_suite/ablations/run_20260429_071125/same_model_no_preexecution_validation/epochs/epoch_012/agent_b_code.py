def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(start):
        dist = [[INF] * h for _ in range(w)]
        x0, y0 = start
        if not valid(x0, y0): return dist
        dist[x0][y0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x = qx[qi]; y = qy[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    # If no resources, retreat from opponent deterministically
    if not resources:
        best = ( -INF, 0, 0 )
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): continue
            dopp = max(abs(nx - ox), abs(ny - oy))
            key = (dopp, -dx, -dy)
            if key > best:
                best = key[0], dx, dy
        return [best[1], best[2]] if (best[0] != -INF) else [0, 0]

    ds = bfs((sx, sy))
    do = bfs((ox, oy))

    # Strategy change: prioritize "get it first"; if none, prioritize minimal self time,
    # while also keeping distance from opponent to reduce their ability to contest.
    best_key = None
    best_t = None
    for rx, ry in resources:
        dS = ds[rx][ry]; dO = do[rx][ry]
        if dS >= INF: 
            continue
        if dO < INF and dS < dO:
            # winning resource: maximize time advantage; tiebreak to nearer
            key = (2, dO - dS, -dS, rx, ry)
        else:
            # no guaranteed win: minimize your time and keep away from opponent
            opp_allow = dO if dO < INF else 20
            key = (1, -dS, opp_allow, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    if best_t is None:
        return [0, 0]
    tx, ty = best_t

    # Move selection: go to the neighbor that improves self distance to target,
    # with tie-breaking by increasing distance from opponent (contest avoidance).
    best_dx, best_dy = 0, 0
    best_val = (-INF, -INF, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny): continue
        if ds[tx][ty] >= INF:
            val1 = 0
        else:
            val1 = -ds[nx][ny]  # reduce our distance to target via dist map
        dopp = max(abs(nx - ox), abs(ny - oy))
        # tie-break deterministically