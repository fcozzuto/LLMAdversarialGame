def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources") or []
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles
    INF = 10**9

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0):
            return dist
        dist[x0][y0] = 0
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    dS = bfs(sx, sy)
    dO = bfs(ox, oy)

    best_target = None
    best_score = -10**18
    scored = False
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not valid(rx, ry):
            continue
        ds, do = dS[rx][ry], dO[rx][ry]
        if ds >= INF:
            continue
        # Prefer resources we can reach sooner, and that opponent reaches later.
        score = (do - ds) * 10 - ds
        # Small bias toward reachable and closer to center for tie-breaking.
        cx, cy = (w - 1) / 2, (h - 1) / 2
        score -= abs(rx - cx) * 0.1 + abs(ry - cy) * 0.1
        if score > best_score:
            best_score = score
            best_target = (rx, ry)
            scored = True

    # If no resource is reachable (or none visible), fallback to improving position.
    if not scored:
        tx, ty = (w - 1) - ox, (h - 1) - oy  # move generally away from opponent corner
        best_move = (0, 0)
        best_val = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            # Avoid opponent, and drift toward center-ish while not hitting obstacles.
            daway = (abs(nx - ox) + abs(ny - oy))
            center_bias = - (abs(nx - (w - 1) / 2) + abs(ny - (h - 1) / 2)) * 0.05
            v = daway + center_bias
            if v > best_val:
                best_val = v
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    rx, ry = best_target
    # Choose the move that minimizes our distance to the target while not making things worse vs opponent.
    best_move = (0, 0)
    best_k = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ns = dS[nx][ny]
        if ns >= INF:
            continue
        nk = -(ns) * 20
        if dO[nx][ny] < INF:
            nk += (dO[rx][ry] - dO[nx][ny]) * 2  # slight pressure
        # Ensure progress toward target (prefer monotonic step closer).
        if valid(rx, ry):
            dcur = dS[sx][sy]
            dnext = dS[nx][ny]
            if dnext < dcur:
                nk += 50
        if nk > best_k:
            best_k = nk
            best_move = (dx, dy)
    return [best_move[0], best_move[1]]