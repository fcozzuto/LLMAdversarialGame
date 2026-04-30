def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    rem = observation.get("remaining_resource_count", len(resources))
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    INF = 10**9
    def bfs(st):
        dist = [[INF]*h for _ in range(w)]
        x0, y0 = st
        if not valid(x0, y0): return dist
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

    ds = bfs((sx, sy))
    do = bfs((ox, oy))
    res = [tuple(r) for r in resources] if resources else []
    rem_factor = 1.0 if rem <= 0 else (1.0 + min(1.5, rem / 12.0))

    cx, cy = 3.5, 3.5
    best_score = -10**18
    best_move = (0, 0)

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny): 
            continue
        self_to_opp = do[nx][ny]
        center_pen = -0.02 * ((nx - cx)*(nx - cx) + (ny - cy)*(ny - cy))
        safety = -0.08 * self_to_opp

        if not res:
            score = safety + center_pen
        else:
            # Prefer resources we can reach strictly earlier; otherwise, contest by maximizing (opp-self).
            # Also add slight deterministic preference to alternate "sides" each epoch cycle.
            side_bias = ((nx + ny + observation["turn_index"]) % 2) * 0.01
            score = safety + center_pen + side_bias
            for rx, ry in res:
                sd = ds[nx][ny] + (0 if (rx, ry) == (nx, ny) else 0)  # no-op, keep structure deterministic
                # Use direct distances