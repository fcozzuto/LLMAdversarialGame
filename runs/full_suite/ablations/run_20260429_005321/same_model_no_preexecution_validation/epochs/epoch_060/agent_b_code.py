def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (not inb(x, y)) or ((x, y) in obs)

    if blocked(sx, sy): return [0, 0]
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**9

    def bfs(start):
        if blocked(start[0], start[1]): return None
        dist = [[INF] * w for _ in range(h)]
        dist[start[1]][start[0]] = 0
        qx = [start[0]]; qy = [start[1]]; qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if not blocked(nx, ny) and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    myd = bfs((sx, sy))
    opd = bfs((ox, oy)) if not blocked(ox, oy) else None
    if myd is None or not resources: return [0, 0]
    if opd is None: opd = [[INF] * w for _ in range(h)]

    best_r = None; best_val = -10**18
    for rx, ry in resources:
        md = myd[ry][rx]; od = opd[ry][rx]
        if md >= INF: 
            continue
        # Prefer resources I can reach sooner than opponent; deny opponent when close.
        val = (od - md) * 100 - md
        if (rx == sx and ry == sy): val = 10**12
        if val > best_val:
            best_val = val; best_r = (rx, ry)
    if best_r is None: return [0, 0]
    tx, ty = best_r

    best_move = [0, 0]; best_mval = -10**18
    curd = myd[sy][sx]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny): 
            continue
        nd = myd[ny][nx]
        if nd >= INF: 
            continue
        # Primary: minimize distance-to-target; Secondary: increase opponent distance-to-target.
        opp_dist = opd[ty][tx] if opd[ty][tx] < INF else INF
        # opponent position after its move is unknown; use current opp proximity as proxy
        my_press = (curd - nd)
        den = (opd[ty][tx] - nd)  # smaller opponent reach helps my-deny indirectly
        mval = my_press * 1000 - nd * 10 + den
        if (nx, ny) == (tx, ty): mval += 10**7
        if mval > best_mval:
            best_mval = mval; best_move = [dx, dy]
    return best_move