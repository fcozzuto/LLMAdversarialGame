def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**8

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(start):
        dist = [[INF] * h for _ in range(w)]
        x0, y0 = start
        if not valid(x0, y0):
            return dist
        dist[x0][y0] = 0
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    distS = bfs((sx, sy))
    distO = bfs((ox, oy))

    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            ds = distS[rx][ry]
            if ds >= INF:
                continue
            do = distO[rx][ry]
            if do >= INF:
                do = INF
            # Prefer being closer than opponent; then prioritize securing sooner; then deterministic tie-break.
            adv = do - ds
            key = (adv, -ds, rx, ry)
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        target = best
    else:
        target = None

    if target is None:
        # Move toward center-ish if no target.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best_move = [0, 0]; best_val = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            val = -((nx - cx) ** 2 + (ny - cy) ** 2)
            if best_val is None or val > best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
                best_val = val
                best_move = [dx, dy]
        return best_move

    tx, ty = target
    # Choose move that minimizes distance to target; tie-break by maximizing advantage to opponent for the target.
    best_move = [0, 0]
    best_ds = distS[sx][sy]
    best_adv = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nds = distS[nx][ny