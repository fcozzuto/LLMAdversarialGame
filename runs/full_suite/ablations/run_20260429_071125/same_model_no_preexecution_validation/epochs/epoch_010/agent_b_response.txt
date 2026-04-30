def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    INF = 10**9
    def bfs(start):
        dist = [[INF] * h for _ in range(w)]
        if not valid(start[0], start[1]): return dist
        sx0, sy0 = start
        dist[sx0][sy0] = 0
        qx = [sx0]; qy = [sy0]; qi = 0
        while qi < len(qx):
            x = qx[qi]; y = qy[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    ds = bfs((sx, sy)) if resources else None
    do = bfs((ox, oy)) if resources else None

    def pick_target():
        best = None
        best_key = -10**18
        for rx, ry in resources:
            dss = ds[rx][ry]
            too = do[rx][ry]
            if dss >= INF: 
                continue
            # Prefer resources we can reach and where we are relatively closer than opponent
            key = (too - dss) * 10 - dss
            if key > best_key:
                best_key = key
                best = (rx, ry, dss, too)
        return best

    target = pick_target() if resources else None

    best_move = (0, 0)
    best_val = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        if target:
            tx, ty, dss, too = target
            myd = ds[nx][ny]
            # Move toward chosen target; also try to increase opponent distance to it
            cur_to_t = ds[tx][ty] if ds[tx][ty] < INF else INF
            # approximate progress: target distance from candidate
            cand_to_t = ds[tx][ty] - (ds[tx][ty] - ds[nx][ny]) if False else ds[tx][ty]
            cand_to_t = ds[nx][ny] + abs(tx - nx) + abs(ty - ny)  # deterministic local proxy
            # Better proxy: if we can, use BFS dist from candidate to target
            # We don't have reverse BFS, but ds[nx][ny] is already from self; still keep tie-breakers.
            opp_to_t = do[tx][ty] if do and do[tx][ty] < INF else INF
            # contest pressure: prefer being closer than opponent by margin
            margin = opp_to_t - cand_to_t if cand_to_t < INF else -INF
            # strong pull toward target
            val = -cand_to_t * 3 + margin * 2 - obs_risk(nx, ny, obstacles, w, h)
        else:
            # No resources: maximize distance from opponent while staying safe
            dopp = abs(nx -