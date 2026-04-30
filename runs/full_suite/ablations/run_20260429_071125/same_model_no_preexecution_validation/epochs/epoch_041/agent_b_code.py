def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    if not resources:
        return [0, 0]

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
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

    distS = bfs(sx, sy)
    distO = bfs(ox, oy)

    # If already on a resource, don't waste time: move to the next best.
    # Main policy: pick a move that maximizes "winning margin" on resources:
    # higher (opp_dist - my_dist) means I can reach before opponent.
    best = (None, -10**18)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        score = 0
        # prioritize nearest opportunities and also prevent the opponent from having an easy grab
        for rx, ry in resources:
            ds = distS[nx][ny] + (0 if (nx, ny) == (rx, ry) else 0)
            do = distO[ox][oy]  # dummy to avoid extra lookup if resources empty (not the case)
            do = distO[rx][ry]
            ds = distS[rx][ry] if (rx, ry) != (nx, ny) else 0
            if ds >= INF or do >= INF:
                continue
            margin = do - ds  # positive means I'm sooner
            # Use a smooth, greedy aggregation: focus on best margin but keep some closeness bias
            score = max(score, margin * 100 - ds)
        # tie-break deterministically toward moving "down-right" preference
        score += (dx + 1) * 0.001 + (dy + 1) * 0.0001
        if score > best[1]:
            best = ((dx, dy), score)

    if best[0] is None:
        return [0, 0]
    return [int(best[0][0]), int(best[0][1])]