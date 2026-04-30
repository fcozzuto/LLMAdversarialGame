def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles
    INF = 10**9
    def bfs(start):
        dist = [[INF]*h for _ in range(w)]
        x0, y0 = start
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
    resources = observation.get("resources") or []
    if not resources:
        # go to safer corner/center-ish deterministically: prefer reducing Chebyshev to center
        cx, cy = (w-1)//2, (h-1)//2
        best = (INF, 0, 0)
        for dx, dy in moves:
            nx, ny = sx+dx, sy+dy
            if not valid(nx, ny): 
                continue
            d = abs(nx-cx); e = abs(ny-cy)
            dd = d if d > e else e
            cand = (dd, -dx, -dy)
            if cand < best:
                best = cand
        return [best[1]*-1 if best[1] else 0, best[2]*-1 if best[2] else 0]  # keep ints
    bestR = None
    bestScore = None
    for rx, ry in resources:
        ds = distS[rx][ry]; do = distO[rx][ry]
        if ds >= INF and do >= INF: 
            continue
        # primary: maximize our advantage (do - ds); secondary: smaller ds; tertiary: larger do
        adv = do - ds if (ds < INF and do < INF) else (999999 if ds < INF else -999999)
        # If we can't reach but opponent can, strongly avoid
        if ds >= INF:
            adv = -999999
        score = (-(adv), ds if ds < INF else INF, -(do if do < INF else -INF), rx, ry)
        if bestScore is None or score < bestScore:
            bestScore = score
            bestR = (rx, ry)
    if bestR is None:
        return [0, 0]
    tx, ty = bestR
    # choose move that decreases distS to target, while also not giving opponent an immediate better claim
    cur = distS[sx][sy]
    bestMove = (INF, 0, 0)
    for dx, dy in moves:
        nx, ny = sx+dx, sy+dy
        if not valid(nx, ny): 
            continue
        dsn = distS[nx][ny]
        don = distO[nx][ny]
        if dsn >= INF: 
            continue
        # penalty if opponent is much closer after our move (discourage walking into their capture)
        cap = don - dsn
        # primary: minimize dsn; secondary: maximize (dsn - do for us) via cap; tertiary: tie-break by direction deterministically
        cand = (dsn, -cap, dx*2 + dy)
        if cand < bestMove:
            bestMove = cand
            bestdx, bestdy = dx, dy
    return [int(bestdx), int(bestdy)]