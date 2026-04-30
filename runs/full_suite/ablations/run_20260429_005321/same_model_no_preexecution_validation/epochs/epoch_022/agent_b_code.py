def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = {(p[0], p[1]) for p in obstacles_list}
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    INF = 10**9

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
    best_move = (0, 0)
    best_overall = -INF
    for dxm, dym in dirs:
        nx, ny = sx + dxm, sy + dym
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        myd_next = bfs((nx, ny))
        best_for_move = -INF
        for rx, ry in resources:
            dm = myd_next[ry][rx]; do = opd[ry][rx]
            if dm >= INF or do >= INF:
                continue
            # Prioritize resources we can reach sooner than opponent; else reduce their lead.
            gap = do - dm
            # Slightly favor shorter ETA to resources.
            score = (gap * 100) - dm
            if score > best_for_move:
                best_for_move = score
        if best_for_move > best_overall:
            best_overall = best_for_move
            best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]