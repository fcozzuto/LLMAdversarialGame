def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def bfs(start):
        x0, y0 = start
        dist = [[INF] * w for _ in range(h)]
        if not inb(x0, y0) or (x0, y0) in obstacles:
            return dist
        dist[y0][x0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    opd = bfs((ox, oy))

    def cheb(x1, y1, x2, y2): 
        dx = x1 - x2; dy = y1 - y2
        return (dx if dx >= 0 else -dx) if (absdx := (dx if dx >= 0 else -dx)) >= (absdy := (dy if dy >= 0 else -dy)) else absdy

    best_move = (0, 0)
    best_key = (-INF, INF, -INF)

    for dxm, dym in dirs:
        nx, ny = sx + dxm, sy + dym
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        myd = bfs((nx, ny))
        opp_proxy = -cheb(nx, ny, ox, oy)
        local_best_gap = -INF
        local_best_time = INF
        for rx, ry in resources:
            myt = myd[ry][rx]
            opt = opd[ry][rx]
            if myt >= INF or opt >= INF:
                continue
            gap = opt - myt
            if gap > local_best_gap or (gap == local_best_gap and myt < local_best_time):
                local_best_gap = gap
                local_best_time = myt
        if local_best_gap == -INF:
            # No reachable resources; just move to increase safety and approach any reachable cell.
            key = (-INF, INF, opp_proxy)
        else:
            key = (local_best_gap, local_best_time, opp_proxy)
        if key[0] > best_key[0] or (key[0] == best_key[0] and (