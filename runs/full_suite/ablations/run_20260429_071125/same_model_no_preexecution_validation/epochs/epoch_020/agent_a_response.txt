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
        dist = [[INF]*h for _ in range(w)]
        x0, y0 = start
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

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (0, 0); bestv = -INF
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            v = -max(abs(nx - tx), abs(ny - ty))
            if v > bestv: bestv = v; best = (dx, dy)
        return [best[0], best[1]]

    best = (0, 0); bestv = -INF
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds = distS[nx][ny]; do = distO[nx][ny]
        if ds >= INF: 
            continue
        # Reward being closer than opponent to valuable future resources.
        v = 0
        for rx, ry in resources:
            dsr = distS[nx][ny] + (0 if (rx == nx and ry == ny) else 0)
            # We avoid extra searches: use direct distance from this step by comparing distances at target.
            dsr = distS[rx][ry]  # base distance from current (equivalent since distS is from start; add next-step ds not needed for ranking)
            dor = distO[rx][ry]
            if dsr >= INF or dor >= INF:
                continue
            # Prefer resources where we can arrive earlier; slightly penalize if opponent is also near.
            v += (dor - dsr) * 100 - dsr
        # Add local tie-breakers: closer to opponent-disrupted area and resources nearby.
        v += (do - ds) * 5
        if v > bestv:
            bestv = v; best = (dx, dy)

    return [best[0], best[1]]