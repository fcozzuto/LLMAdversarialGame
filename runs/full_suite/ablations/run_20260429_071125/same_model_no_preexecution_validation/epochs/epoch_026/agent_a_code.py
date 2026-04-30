def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((int(p[0]), int(p[1])) for p in obs_list)
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**8

    def inb(x,y): return 0 <= x < w and 0 <= y < h
    def valid(x,y): return inb(x,y) and (x,y) not in obstacles
    def bfs(start):
        x0, y0 = start
        dist = [[INF]*h for _ in range(w)]
        if not valid(x0,y0): return dist
        dist[x0][y0] = 0
        q = [(x0,y0)]; qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x+dx, y+dy
                if valid(nx,ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx,ny))
        return dist

    distS = bfs((sx,sy)); distO = bfs((ox,oy))

    if not resources:
        tx, ty = (w-1)//2, (h-1)//2
        best = None; best_move = (0,0)
        for dx, dy in moves:
            nx, ny = sx+dx, sy+dy
            if not valid(nx,ny): continue
            key = (-(abs(nx-tx)+abs(ny-ty)),)
            if best is None or key > best:
                best = key; best_move = (dx,dy)
        return [int(best_move[0]), int(best_move[1])]

    best_res = None
    for rx, ry in resources:
        ds = distS[rx][ry]; do = distO[rx][ry]
        if ds >= INF and do >= INF: 
            continue
        ds2 = ds if ds < INF else INF
        do2 = do if do < INF else INF
        advantage = (do2 - ds2) if (ds2 < INF) else -INF
        # Prefer resources we can reach no later than opponent; otherwise prefer largest advantage.
        key = (0 if (ds2 <= do2) else -1, advantage, -ds2, -abs(rx - ox) - abs(ry - oy), -abs(rx - sx) - abs(ry - sy), rx, ry)
        if best_res is None or key > best_res[0]:
            best_res = (key, (rx,ry))

    _, (tx, ty) = best_res
    best_key = None; best_move = (0,0)
    for dx, dy in moves:
        nx, ny = sx+dx, sy+dy
        if not valid(nx,ny): continue
        myd = distS[nx][ny]
        if myd >= INF: 
            continue
        # Evaluate move by progress toward target and by potentially delaying opponent on that target.
        my_to_t = myd + (distS[tx][ty] - distS[sx][sy] if distS[sx][sy] < INF and distS[tx][ty] < INF else 0)
        opp_to_t = distO[tx][ty]
        # Approximate: move that reduces distance to target; if tie, pick moves that improve relative arrival.
        key = (-(abs(nx-tx)+abs(ny-ty)),
               (opp_to_t - distS[nx][ny]) if distS[nx][ny] < INF else -INF,
               -distS[nx][ny], nx, ny)
        if best_key is None or key > best_key:
            best_key = key; best_move = (dx,dy)
    return [int(best_move[0]), int(best_move[1])]