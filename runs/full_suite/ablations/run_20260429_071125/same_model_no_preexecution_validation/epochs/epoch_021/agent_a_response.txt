def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles
    INF = 10**8

    def bfs(start):
        x0, y0 = start
        dist = [[INF]*h for _ in range(w)]
        if not valid(x0, y0): return dist
        dist[x0][y0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    distS = bfs((sx, sy))
    distO = bfs((ox, oy))

    if not resources:
        tx, ty = (w-1)//2, (h-1)//2
        best = (0,0); bestv = -INF
        for dx, dy in moves:
            nx, ny = sx+dx, sy+dy
            if not valid(nx, ny): continue
            v = -((nx-tx)*(nx-tx) + (ny-ty)*(ny-ty))
            if v > bestv: bestv = v; best = (dx, dy)
        return [best[0], best[1]]

    res = [(r[0], r[1]) for r in resources if valid(r[0], r[1])]
    if not res:
        return [0, 0]

    def best_target(x, y):
        best = None; bestv = INF
        for rx, ry in res:
            ds = distS[rx][ry] if distS[rx][ry] < INF else INF
            do = distO[rx][ry] if distO[rx][ry] < INF else INF
            if ds == INF: continue
            # Prefer targets closer to us and farther from opponent (deterministic)
            key = ds*2 + (0 if do == INF else do)
            if key < bestv or (key == bestv and (rx, ry) < best):
                bestv = key; best = (rx, ry)
        return best

    # Anchor target choice from current state (avoids churning)
    target = best_target(sx, sy)
    if target is None:
        return [0, 0]
    tx, ty = target

    cur_ds = distS[tx][ty]
    cur_do = distO[tx][ty]

    best_move = (0, 0)
    best_score = -INF

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny): continue
        ds_new = distS[nx][ny]
        if ds_new >= INF: continue

        # Estimate time advantage at our chosen target using distance maps
        # (Assumes monotonic in shortest-path distance to target.)
        distS_to_target = distS[tx][ty]
        if distS_to_target >= INF: continue
        # Use our move to reduce effective arrival by local progress proxy:
        # favor moves that get us closer to the target (Manhattan-aligned).
        man_closer = (abs(sx-tx)+abs(sy-ty)) - (abs(nx-tx)+abs(ny-ty))

        # Opponent pressure: favor moves that increase opponent distance to our target
        # and that reduce opponent access to other resources if close.
        do_to_target = distO[tx][ty]
        pressure = -do_to_target

        # Secondary: consider best alternative target for opponent vs us
        # by evaluating min opponent distance among resources.
        best_opp = INF
        for rx, ry in res:
            if distO[rx][ry] < best