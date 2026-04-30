def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(start):
        x0, y0 = start
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0): return dist
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

    distS = bfs((sx, sy))
    distO = bfs((ox, oy))

    best_r = None
    best_key = None
    for rx, ry in resources:
        ds = distS[rx][ry]
        if ds >= INF: 
            continue
        do = distO[rx][ry]
        adv = (do - ds) if do < INF else (10**6 - ds)
        key = (adv, -ds, -rx, -ry)  # deterministic tie-break
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    if best_r is None:
        best_move = (0, 0); best_cmp = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): nx, ny = sx, sy
            # if can move, bias to not approach opponent
            dOpp = abs(nx - ox) + abs(ny - oy)
            key = (-dOpp, nx, ny)
            if best_cmp is None or key > best_cmp:
                best_cmp = key; best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    tx, ty = best_r
    best_move = (0, 0)
    best_cmp = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0
        ds_next = distS[nx][ny]
        do_next = distO[nx][ny] if distO[nx][ny] < INF else INF
        # prioritize getting closer to