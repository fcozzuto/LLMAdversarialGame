def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles
    INF = 10**9
    def bfs(start):
        x0, y0 = start
        dist = [[INF]*h for _ in range(w)]
        if not valid(x0, y0): return dist
        dist[x0][y0] = 0
        q = [(x0, y0)]; qi = 0
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

    def res_value(x, y):
        if not valid(x, y): return -INF
        ds = distS[x][y]; do = distO[x][y]
        if ds >= INF: return -INF
        # Prefer resources where we arrive sooner than opponent; break ties toward smaller ds.
        return (do - ds) * 100 - ds

    best_move = (0, 0); best_val = -INF
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        v = -INF
        if valid(nx, ny):
            # Evaluate immediate position toward best reachable resource.
            for rx, ry in resources:
                if valid(rx, ry):
                    # Approximate by comparing our distance from next position to resource.
                    ds_next = bfs((nx, ny))[rx][ry] if (rx != nx or ry != ny) else 0
                    if ds_next < INF:
                        do = distO[rx][ry]
                        if do < INF:
                            v = max(v, (do - ds_next) * 100 - ds_next)
        if v > best_val or (v == best_val and (dx, dy) < best_move):
            best_val = v; best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]