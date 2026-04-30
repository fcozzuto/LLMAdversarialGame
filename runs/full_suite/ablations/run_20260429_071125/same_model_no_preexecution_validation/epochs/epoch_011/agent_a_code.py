def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x,y): return 0 <= x < w and 0 <= y < h
    def valid(x,y): return inb(x,y) and (x,y) not in obstacles
    INF = 10**9

    if not resources:
        candidates = []
        for dx, dy in moves:
            nx, ny = sx+dx, sy+dy
            if not valid(nx, ny): 
                continue
            d = max(abs(nx-ox), abs(ny-oy))
            candidates.append((d, dx, dy))
        candidates.sort(key=lambda t:(-t[0], t[1], t[2]))
        return [candidates[0][1], candidates[0][2]] if candidates else [0,0]

    def bfs(start):
        dist = [[INF]*h for _ in range(w)]
        x0,y0 = start
        if not valid(x0,y0):
            return dist
        dist[x0][y0] = 0
        qx=[x0]; qy=[y0]; qi=0
        while qi < len(qx):
            x=qx[qi]; y=qy[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x+dx, y+dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    ds = bfs((sx, sy))
    do = bfs((ox, oy))

    # Choose a target that favors both reachability and relative advantage.
    # New vs prior epoch: prioritize opponent-forcing targets (big "do - ds") and
    # add a light obstacle-adjacency bias to avoid being lured into dead zones.
    def obst_adj(x,y):
        c = 0
        for dx, dy in [(-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1)]:
            nx, ny = x+dx, y+dy
            if inb(nx, ny) and (nx, ny) in obstacles:
                c += 1
        return c

    best = None
    best_score = -10**18
    for rx, ry in resources:
        d1 = ds[rx][ry]; d2 = do[rx][ry]
        if d1 >= INF: 
            continue
        if d2 >= INF:
            rel = 6  # strongly prefer unreachables for opponent
        else:
            rel = d2 - d1  # positive means we arrive earlier
        # Prefer closer resources but strongly reward winning races.
        score = (rel * 1000) - (d1 * 10) - (obst_adj(rx, ry) * 2)
        # Deterministic tie-break: smaller coordinates
        if score > best_score or (score == best_score and (rx,ry) < best):
            best_score = score
            best = (rx, ry)

    tx, ty = best
    # Evaluate next step by best expected progress, plus opponent distancing.
    def step_cost(nx, ny):
        myd = ds[tx][ty]
        if myd >= INF:
            myd = max(abs(nx-tx), abs(ny-ty))
        nds = ds[nx][ny] if valid(nx, ny) else INF
        # progress: reduce own distance to target (using ds if possible)
        prog = nds - ds[tx][ty]  # smaller is better (exact not required)
        # race pressure: increase opponent distance to target if possible
        odd = do[tx][ty] if do[tx][ty] < INF else 999
        opp_seek = max(abs(ox-tx), abs(oy-ty))
        # local safety: keep farther from opponent to avoid head-on contests
        sep = max(abs(nx-ox), abs(ny-oy))
        return (prog * 3) - (sep * 1) - ((odd - opp_seek) * 0.05)

    best_move = (0,0)
    best