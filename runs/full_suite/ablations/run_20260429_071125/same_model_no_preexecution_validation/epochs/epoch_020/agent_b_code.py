def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
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

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    def center_bias(x, y):
        dx = x - cx; dy = y - cy
        return -(dx*dx + dy*dy)

    def resource_value(x, y):
        ds = distS[x][y]; do = distO[x][y]
        if ds >= INF and do >= INF: return -INF
        if ds >= INF: return -INF
        if do >= INF: do = ds + 6  # ensure strong preference
        # Aim to be earlier than opponent; slightly prefer positions farther from opponent if close.
        lead = do - ds
        opp_close_pen = -abs(x - ox) - abs(y - oy)
        return lead*120 - ds*8 + opp_close_pen + center_bias(x, y)

    best_move = (0, 0); best_val = -INF
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny): continue
        # Primary: best achievable resource value from next position (approx: current next pos value).
        val = -INF
        for rx, ry in resources:
            if not valid(rx, ry): continue
            # approximate: if we move to (nx,ny), our effective distance to (rx,ry) is ds at (rx,ry) minus 1 if beneficial
            # deterministic approximation: use resource_value at (rx,ry) minus a small step penalty if we wouldn't reach quickly.
            v = resource_value(rx, ry) - (distS[nx][ny] if distS[nx][ny] < INF else 10**6)
            if v > val: val = v
        if val == -INF:
            # Fallback: go toward center while keeping away from obstacles (via dist to self is already safe).
            if valid(nx, ny):
                v2 = center_bias(nx, ny) - (abs(nx - ox) + abs(ny - oy))*2
                val = v2
        # Tie-break deterministically: prefer staying if equally good, else lexicographic move preference.
        if val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val; best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]