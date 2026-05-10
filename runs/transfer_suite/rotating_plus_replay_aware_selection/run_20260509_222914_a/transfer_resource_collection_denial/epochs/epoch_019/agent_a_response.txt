def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    x, y = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    deltas = [(-1, 0),(1, 0),(0, -1),(0, 1),(-1,-1),(1,-1),(-1, 1),(1, 1),(0, 0)]
    move_order = {(-1, 0):0,(1, 0):1,(0,-1):2,(0, 1):3,(-1,-1):4,(1,-1):5,(-1,1):6,(1,1):7,(0,0):8}
    def inb(a,b): return 0 <= a < w and 0 <= b < h and (a,b) not in obstacles
    def bfs(sx, sy):
        INF = 10**9
        dist = [[INF]*w for _ in range(h)]
        qx = [sx]; qy = [sy]; qh = 0
        dist[sy][sx] = 0
        while qh < len(qx):
            cx, cy = qx[qh], qy[qh]; qh += 1
            nd = dist[cy][cx] + 1
            for dx,dy in deltas:
                nx, ny = cx+dx, cy+dy
                if inb(nx, ny) and dist[ny][nx] > nd:
                    dist[ny][nx] = nd
                    qx.append(nx); qy.append(ny)
        return dist
    if not resources:
        tx, ty = w//2, h//2
        dx = 0 if tx == x else (1 if tx > x else -1)
        dy = 0 if ty == y else (1 if ty > y else -1)
        candidates = []
        for ddx, ddy in deltas:
            nx, ny = x+ddx, y+ddy
            if inb(nx, ny):
                candidates.append((abs(nx-tx)+abs(ny-ty), move_order[(ddx,ddy)], ddx, ddy))
        candidates.sort()
        return [candidates[0][2], candidates[0][3]] if candidates else [0,0]

    ds = bfs(x, y)
    do = bfs(ox, oy)
    INF = 10**9
    best_val = -10**18
    best = [0, 0]
    for dx, dy in deltas:
        nx, ny = x+dx, y+dy
        if not inb(nx, ny): 
            continue
        self_dist_cell = ds[ny][nx]
        val = 0
        # evaluate by best resource swing (opponent minus self), deterministic over resources
        best_swing = -10**18
        nearest_self = INF
        for rx, ry in resources:
            sd = ds[ry][nx]
            od = do[ry][ox]  # opponent at fixed position each turn
            if sd >= INF: 
                continue
            nearest_self = sd if sd < nearest_self else nearest_self
            swing = od - sd
            if swing > best_swing:
                best_swing = swing
        val = best_swing
        if val > best_val or (val == best_val and move_order[(dx,dy)] < move_order[tuple(best)]):
            best_val = val
            best = [dx, dy]
    return best