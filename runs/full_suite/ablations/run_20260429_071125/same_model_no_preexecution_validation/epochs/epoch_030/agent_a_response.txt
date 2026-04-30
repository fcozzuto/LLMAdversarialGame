def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = map(int, observation["self_position"])
    ox, oy = map(int, observation["opponent_position"])
    resources = observation.get("resources") or []
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

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

    def best_target():
        best = None
        best_key = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            if not valid(rx, ry): 
                continue
            ds = distS[rx][ry]; do = distO[rx][ry]
            if ds >= INF and do >= INF:
                continue
            # Prefer resources we can reach no later than opponent; otherwise race the closest-to-tie ones.
            if ds <= do:
                key = (0, ds, -(do - ds))  # win-tie: smallest ds, then largest gap
            else:
                key = (1, ds - do, ds)     # opponent ahead: smallest (ds-do), then smaller ds
            if best_key is None or key < best_key:
                best_key = key
                best = (rx, ry, ds, do)
        return best

    tgt = best_target()
    if not tgt:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best_move = (0, 0); best_d = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            d = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
            if best_d is None or d < best_d:
                best_d = d; best_move = [dx, dy]
        return best_move

    rx, ry, ds, do = tgt

    # Move selection: reduce our distance to the target, and slightly increase opponent's distance to it (deterministic tie-break).
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        my = distS[nx][ny] + 0  # keeps deterministic structure
        # Use gradient-like proxy: compare our path length to target through current cell.
        my_to_t = distS[nx][ny] + max(0, distS[rx][ry] - distS[rx][ry])