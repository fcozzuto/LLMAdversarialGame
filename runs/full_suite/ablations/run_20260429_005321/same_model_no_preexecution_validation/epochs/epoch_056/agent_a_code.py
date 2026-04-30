def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (not inb(x, y)) or ((x, y) in obs)

    if blocked(sx, sy) or not resources:
        return [0, 0]

    INF = 10**9
    def bfs(start):
        if blocked(start[0], start[1]): return None
        dist = [[INF]*w for _ in range(h)]
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
    opd = bfs((ox, oy))
    if myd is None:
        return [0, 0]
    if opd is None:
        opd = [[INF]*w for _ in range(h)]

    best = None
    best_adv = -INF
    best_my = INF
    for rx, ry in resources:
        d1 = myd[ry][rx]
        d2 = opd[ry][rx]
        if d1 >= INF: 
            continue
        adv = d2 - d1  # positive means I reach earlier (or opponent unreachable)
        if adv > best_adv or (adv == best_adv and d1 < best_my):
            best_adv = adv
            best_my = d1
            best = (rx, ry)
    if best is None:
        return [0, 0]

    tx, ty = best
    cur_my = myd[sy][sx]
    cur_opd = opd[sy][sx]
    best_move = (0, 0)
    best_key = None

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        nm = myd[ny][nx]
        no = opd[ny][nx]
        # Prefer decreasing my distance to target; then increasing eventual advantage.
        key = (nm - cur_my, -(no - nm), nm, dx, dy)
        if best_key is None or key < best_key:
            best_key = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]