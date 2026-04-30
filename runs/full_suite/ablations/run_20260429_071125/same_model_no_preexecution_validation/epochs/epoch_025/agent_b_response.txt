def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((int(p[0]), int(p[1])) for p in obs_list)
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**9

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def bfs(start):
        x0, y0 = start
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0):
            return dist
        dist[x0][y0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x = qx[qi]; y = qy[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    distS = bfs((sx, sy))
    distO = bfs((ox, oy))

    # Pick best resource by (how much earlier we arrive than opponent), then by closer to us, then lexicographic.
    best = None
    for rx, ry in resources:
        ds = distS[rx][ry]
        if ds >= INF:
            continue
        do = distO[rx][ry]
        if do >= INF:
            adv = 10**6
        else:
            adv = do - ds
        key = (adv, -ds, -rx, -ry)
        if best is None or key > best[0]:
            best = (key, (rx, ry))
    if best is None:
        # No reachable resources: move to maximize distance from opponent (simple deterministic).
        best_move = (0, 0); best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dmin = max(0, abs(nx - ox) + abs(ny - oy))
            sc = (dmin, -abs(dx), -abs(dy), dx, dy)
            if best_score is None or sc > best_score:
                best_score = sc; best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    tx, ty = best[1]
    cur_ds = distS[sx][sy]

    # Choose a step that reduces distance to target; break ties by improving advantage at the target.
    best_move = (0, 0)
    best_sc = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nds = distS[nx][ny]
        if nds >= INF:
            continue
        ndo = distO[tx][ty]  # constant, but keep for clarity
        do_here = distO[nx][ny]  # who can reach this cell sooner
        if do_here >= INF:
            do_term = 10**6
        else:
            do_term = do_here
        # Prefer closer to target; if equal, prefer cell where opponent is not closer.
        sc = (-nds, -(do_term - nds), -abs(nx - tx) - abs(ny - ty), dx, dy, -cur_ds)
        if best_sc is None or sc > best_sc:
            best_sc = sc; best_move = (dx, dy)
    return [best_move[0], best_move[1]]