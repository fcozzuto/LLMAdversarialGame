def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles", []) or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def bfs(start):
        sx0, sy0 = start
        if not inside(sx0, sy0):
            return None
        INF = 10**9
        dist = [[INF]*h for _ in range(w)]
        dist[sx0][sy0] = 0
        q = [(sx0, sy0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            d = dist[x][y] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inside(nx, ny) and d < dist[nx][ny]:
                    dist[nx][ny] = d
                    q.append((nx, ny))
        return dist

    my_dist = bfs((sx, sy))
    op_dist = bfs((ox, oy))
    if not resources or my_dist is None or op_dist is None:
        return [0, 0]

    INF = 10**9
    best_r = None
    best_key = None
    for rx, ry in resources:
        d1 = my_dist[rx][ry]
        d2 = op_dist[rx][ry]
        if d1 >= INF or d2 >= INF:
            continue
        lead = d2 - d1
        key = (lead, -d1, -d2, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    if best_r is None:
        return [0, 0]
    tx, ty = best_r

    best_move = (0, 0)
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        # Evaluate local advantage using distance-to-target plus "pressure" on opponent.
        nd1 = my_dist[nx][ny]  # distance from us to our current cell (monotone-ish via BFS)
        # More directly, use distances from each next position to the target.
        d1t = my_dist[nx][ny]
        # Prefer smaller distance to target computed via BFS distances from target not available; approximate by chebyshev to target.
        # But we already have my_dist as from start, so use chebyshev to target for guidance deterministically.
        cheb = lambda x1, y1, x2, y2: (abs(x1-x2) if abs(x1-x2) > abs(y1-y2) else abs(y1-y2))
        my_to_t = cheb(nx, ny, tx, ty)
        op_to_t = cheb(ox, oy, tx, ty)
        val = (op_to_t - my_to_t, -my_to_t, -nd1, -dx, -dy)
        if best_val is None or val > best_val:
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]