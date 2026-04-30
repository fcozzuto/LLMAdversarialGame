def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x,y): return 0 <= x < w and 0 <= y < h
    def valid(x,y): return inb(x,y) and (x,y) not in obstacles
    INF = 10**9

    def bfs(start):
        dist = [[INF]*h for _ in range(w)]
        x0,y0 = start
        if not valid(x0,y0): return dist
        dist[x0][y0] = 0
        q = [(x0,y0)]
        qi = 0
        while qi < len(q):
            x,y = q[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx,dy in moves:
                nx,ny = x+dx,y+dy
                if valid(nx,ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx,ny))
        return dist

    dS = bfs((sx,sy))
    dO = bfs((ox,oy))

    # If no resources, maximize distance from opponent with safe move
    if not resources:
        best = None
        for dx,dy in moves:
            nx,ny = sx+dx, sy+dy
            if not valid(nx,ny): continue
            score = (max(abs(nx-ox), abs(ny-oy)), - (abs(dx)+abs(dy)), 0)
            cand = (score, dx, dy)
            if best is None or cand[0] > best[0]:
                best = cand
        return [best[1], best[2]] if best is not None else [0,0]

    # Target resources: quick enough for us, but hard for opponent (deny)
    best_key = None
    best_target = None
    for (rx,ry) in resources:
        ds = dS[rx][ry]; do = dO[rx][ry]
        if ds >= INF: 
            continue
        # Prefer we can arrive not much later than opponent, and pick cells opponent can't reach soon
        deny = do - ds
        # Also mildly prefer resources closer to center to reduce tie loops
        center_bias = - (abs(rx-(w-1)/2) + abs(ry-(h-1)/2)) * 0.01
        key = (ds, -deny, -center_bias, rx, ry)
        if best_key is None or key < best_key:
            best_key = key; best_target = (rx,ry)

    tx,ty = best_target if best_target is not None else (sx,sy)

    # Choose next step that reduces distance to target while staying safe and not too close to opponent
    curd = dS[tx][ty]
    best_move = None
    for dx,dy in moves:
        nx,ny = sx+dx, sy+dy
        if not valid(nx,ny): 
            continue
        nd = dS[nx][ny]
        # Only consider moves that progress (or equal if all blocked)
        progress = nd - (curd - 1)
        dist_to_opp = max(abs(nx-ox), abs(ny-oy))
        key = (progress, -dist_to_opp, nd, dx, dy)
        if best_move is None or key < best_move[0]:
            best_move = (key, dx, dy)

    return [best_move[1], best_move[2]] if best_move is not None else [0,0]