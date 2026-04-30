def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    INF = 10**9

    def bfs(start):
        x0, y0 = start
        if not inb(x0, y0) or (x0, y0) in obstacles:
            return None
        dist = [[INF] * w for _ in range(h)]
        dist[y0][x0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x = qx[qi]; y = qy[qi]; qi += 1
            d = dist[y][x]
            nd = d + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    mydist0 = bfs((sx, sy))
    opd = bfs((ox, oy))
    if mydist0 is None or opd is None:
        return [0, 0]

    res_set = set((r[0], r[1]) for r in resources)
    res_list = [(r[0], r[1]) for r in resources if inb(r[0], r[1]) and (r[0], r[1]) not in obstacles]
    if not res_list:
        return [0, 0]

    def best_from(x, y, mydist):
        best = -10**18
        for rx, ry in res_list:
            md = mydist[ry][rx]
            od = opd[ry][rx]
            if md >= INF:
                continue
            v = (od - md) - 0.05 * md
            if md == od:
                v -= 0.01 * (abs(rx - ox) + abs(ry - oy))
            if (rx, ry) == (x, y):
                v += 1000.0
            best = v if v > best else best
        return best

    # compute next positions and pick deterministically by best value then direction order
    move_order = dirs  # deterministic
    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in move_order:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # local recomputation from neighbor: BFS from up to 9 positions (small grid)
        mydist = bfs((nx, ny))
        if mydist is None:
            continue
        v = best_from(nx, ny, mydist)
        if v > best_val:
            best_val = v
            best_move = [dx, dy]
    return best_move if best_move is not None else [0, 0]