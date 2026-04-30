def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources") or []
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0): return dist
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

    dO = bfs(ox, oy)
    if not resources:
        # Drift to center while keeping distance from opponent when possible
        cx, cy = w // 2, h // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): nx, ny = sx, sy
            score = -((nx - cx) ** 2 + (ny - cy) ** 2) + 0.01 * (((nx - ox) ** 2 + (ny - oy) ** 2) ** 0.5)
            if best is None or score > best[0] or (score == best[0] and (dx, dy) < best[1]):
                best = (score, (dx, dy))
        return list(best[1])

    # Evaluate each candidate move by resulting position's best resource advantage
    best_move = (0, 0)
    best_score = -INF
    best_tie = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny): nx, ny = sx, sy
        dS = bfs(nx, ny)
        # Targeting heuristic: maximize (opponent_arrival - our_arrival), prefer shorter, avoid dead-ends via reachability
        cur_best = -INF
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            ds = dS[rx][ry]
            do = dO[rx][ry]
            if ds >= INF or do >= INF: 
                continue
            # If we can reach this resource, value it strongly; also slightly prefer being closer than opponent
            adv = do - ds
            val = 1000 * (adv > 0) + 10 * adv - ds
            # Small deterministic bias to reduce oscillations: prefer moves that align toward the resource from our current position
            val += -0.001 * ((nx - rx) ** 2 + (ny - ry) ** 2)
            if val > cur_best:
                cur_best = val
        # If no resources reachable from this move, deprioritize but keep deterministic ordering
        if cur_best == -INF:
            cur_score = -INF / 2
        else:
            cur_score = cur_best
        if cur_score > best_score or (cur_score == best_score and (dx, dy) < best_move):
            best_score = cur_score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]