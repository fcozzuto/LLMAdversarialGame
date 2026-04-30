def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((int(p[0]), int(p[1])) for p in obs_list)

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**8

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(start):
        x0, y0 = start
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0):
            return dist
        dist[x0][y0] = 0
        qx, qy = [x0], [y0]
        qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    distS = bfs((sx, sy))
    distO = bfs((ox, oy))

    # Choose a target resource where we are not behind; else the resource where we can "catch up" most.
    best = None
    for rx, ry in resources:
        ds = distS[rx][ry]
        if ds >= INF: 
            continue
        do = distO[rx][ry]
        adv = do - ds  # positive means we arrive earlier
        # Prefer resources we can reach; primary: maximize advantage, secondary: minimize our time
        if best is None:
            best = (adv, -ds, rx, ry)
        else:
            cand = (adv, -ds, rx, ry)
            if cand > best:
                best = cand

    # Fallback if no reachable resources: head toward center deterministically
    if best is None:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best_move = (0, 0)
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            key = (abs(nx - tx) + abs(ny - ty), abs(nx - ox) + abs(ny - oy), dx, dy)
            if best_key is None or key < best_key:
                best_key = key; best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    _, _, tx, ty = best

    # Pick move that minimizes our distance to target; break ties by maximizing our advantage and keeping away from walls is implicit via validity.
    cur_ds = distS[sx][sy]
    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny): 
            continue
        nds = distS[nx][ny]
        ndo = distO[nx][ny]
        # Primary: decrease our remaining distance (or keep same if forced); Secondary: improve (ndo-nds); then deterministic tie by dx,dy
        key = (nds, -(ndo - nds), abs((nx - tx)) + abs((ny - ty)), dx, dy)
        if best_key is None or key < best_key:
            best_key = key; best_move = (dx, dy)

    # If everything invalid (shouldn't), stay still
    if best_key is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]