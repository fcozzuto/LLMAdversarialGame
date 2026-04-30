def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**8

    def inb(x,y): return 0 <= x < w and 0 <= y < h
    def valid(x,y): return inb(x,y) and (x,y) not in obstacles

    def bfs(start):
        x0,y0 = start
        dist = [[INF]*h for _ in range(w)]
        if not valid(x0,y0): return dist
        dist[x0][y0]=0
        q=[(x0,y0)]
        qi=0
        while qi < len(q):
            x,y=q[qi]; qi+=1
            nd=dist[x][y]+1
            for dx,dy in moves:
                nx,ny=x+dx,y+dy
                if valid(nx,ny) and nd < dist[nx][ny]:
                    dist[nx][ny]=nd
                    q.append((nx,ny))
        return dist

    distS = bfs((sx,sy)); distO = bfs((ox,oy))

    if not resources:
        best = (-(distO[sx][sy]), 0, 0)
        for dx,dy in moves:
            nx,ny = sx+dx, sy+dy
            if not valid(nx,ny): continue
            key = (-distO[nx][ny], abs(nx-w//2)+abs(ny-h//2), nx, ny)
            if key < best:
                best = key; best_move = [dx,dy]
        return best_move if 'best_move' in locals() else [0,0]

    # Pick a resource where we beat opponent; otherwise the least-losing one (maximize do-ds).
    best_res = None
    best_key = None
    for rx,ry in resources:
        ds = distS[rx][ry]; do = distO[rx][ry]
        if ds >= INF: 
            continue
        if do > ds:
            adv = do - ds
            key = (-1, -adv, ds, rx, ry)  # prioritize winning, then bigger margin
        elif do >= INF:
            key = (-1, 10**6, ds, rx, ry)  # opponent unreachable => effectively win
        else:
            # Losing: maximize (do-ds) and then minimize our ds
            key = (0, -(do - ds), ds, rx, ry)
        if best_key is None or key < best_key:
            best_key = key; best_res = (rx,ry)

    rx,ry = best_res
    # Move one step along decreasing our distance; if tie, choose that also increases opponent distance.
    candidates = []
    for dx,dy in moves:
        nx,ny = sx+dx, sy+dy
        if not valid(nx,ny): 
            continue
        candidates.append((distS[nx][ny], -distO[nx][ny], abs(nx-rx)+abs(ny-ry), nx, ny, dx, dy))
    if not candidates:
        return [0,0]
    candidates.sort()
    return [candidates[0][5], candidates[0][6]]