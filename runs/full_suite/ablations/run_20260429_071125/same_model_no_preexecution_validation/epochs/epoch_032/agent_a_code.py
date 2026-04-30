def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = map(int, observation["self_position"])
    ox, oy = map(int, observation["opponent_position"])
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    def inb(x,y): return 0 <= x < w and 0 <= y < h
    def valid(x,y): return inb(x,y) and (x,y) not in obstacles

    INF = 10**9
    def bfs(start):
        x0, y0 = start
        dist = [[INF]*h for _ in range(w)]
        if not valid(x0,y0): return dist
        dist[x0][y0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x = qx[qi]; y = qy[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx = x + dx; ny = y + dy
                if valid(nx,ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    distS = bfs((sx, sy))
    distO = bfs((ox, oy))
    resources = observation.get("resources") or []

    best = None
    best_key = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not valid(rx,ry): 
            continue
        ds = distS[rx][ry]; do = distO[rx][ry]
        if ds >= INF: 
            continue
        # Prefer targets we can reach strictly before opponent; if not, still prefer low ds and high ds-do.
        key = (-(ds < do), (do - ds), -ds, -(rx*10+ry))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    # If we have a target, step greedily on shortest path to it.
    tx, ty = (best if best is not None else (ox, oy))
    curd = distS[tx][ty] if valid(tx,ty) else INF
    best_move = (0, 0)
    best_mkey = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx,ny): 
            continue
        if distS[nx][ny] >= INF:
            continue
        # Move that decreases distance to target; break ties by increasing distance advantage over opponent.
        nd_to_t = abs(distS[nx][ny] - (curd - 1))  # prefers being one closer without exact path tracking
        opp_adv = distO[nx][ny] - distS[nx][ny]  # higher means we are "closer" relative to opponent
        key = (-nd_to_t, -distS[nx][ny], opp_adv, nx*10+ny)
        if best_mkey is None or key > best_mkey:
            best_mkey = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]