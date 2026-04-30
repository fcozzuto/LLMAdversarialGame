def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(start):
        x0, y0 = int(start[0]), int(start[1])
        dist = [[INF] * h for _ in range(w)]
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

    # If no resources, drift toward center deterministically.
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (INF, None)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            d = abs(nx - cx) + abs(ny - cy)
            if d < best[0]: best = (d, (dx, dy))
        return best[1] if best[1] is not None else [0, 0]

    best_step = (0, 0)
    best_target = None
    best_score = -10**30

    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not valid(rx, ry): 
            continue
        ds = distS[rx][ry]; do = distO[rx][ry]
        if ds >= INF: 
            continue
        if do >= INF: 
            do = INF // 2
        # Prefer targets where opponent is significantly worse; also prefer closer.
        score = (do - ds) * 1000 - ds
        # Secondary tie-break: slightly prefer resources nearer our direction of travel to intercept.
        score += -((sx - rx) * (ox - rx) + (sy - ry) * (oy - ry)) * 0.01
        if score > best_score:
            best_score = score
            best_target = (rx, ry)

    rx, ry = best_target
    # Choose a move that minimizes our distance to the target; keep deterministic tie-break ordering.
    best_d = INF
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = distS[nx][ny] + (distS[rx][ry] - distS[nx][ny])  # equals distS[rx][ry] if computed path-consistent
        # Realize preference via direct dist to target by small BFS estimate using distS only:
        # Use Chebyshev heuristic when exact not monotone under obstacles.
        d2 = abs(nx - rx); 
        e2 = abs(ny - ry)
        cheb = d2 if d2 > e2 else e2
        val = (cheb, distS[nx][ny])
        if val < (best_d, INF):
            best_d = val[0]
            best_step = (dx, dy)

    # If target-step somehow invalid, fall back to safe move (stay if all blocked).
    nx, ny = sx + best_step[0], sy + best_step[1]
    if not valid(nx, ny):
        for dx, dy in moves:
            if valid(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    return [int(best_step[0]), int(best_step[1])]