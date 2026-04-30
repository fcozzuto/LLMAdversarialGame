def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h

    INF = 10**9
    def bfs(start):
        x0, y0 = start
        dist = [[INF] * w for _ in range(h)]
        if not inb(x0, y0) or (x0, y0) in obstacles:
            return dist
        dist[y0][x0] = 0
        q = [(x0, y0)]; qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    q.append((nx, ny))
        return dist

    if resources:
        resset = set((r[0], r[1]) for r in resources)
    legal = [(dx, dy) for dx, dy in dirs if inb(sx + dx, sy + dy) and (sx + dx, sy + dy) not in obstacles]
    if not legal:
        return [0, 0]
    if resources:
        for dx, dy in legal:
            if (sx + dx, sy + dy) in resset:
                return [dx, dy]

    our_dist = bfs((sx, sy))
    opp_dist = bfs((ox, oy))

    best = None
    best_sc = -10**18
    for dx, dy in legal:
        nx, ny = sx + dx, sy + dy
        # prefer states where we can beat opponent to resources; if none, minimize opponent's best "lead"
        sc = 0
        for rx, ry in resources:
            d1 = our_dist[ry][rx]; d2 = opp_dist[ry][rx]
            if d1 >= INF or d2 >= INF:
                continue
            # after moving, our distance to resource should be non-increasing in a shortest-path sense; approximate by neighbor effect
            nd1 = d1
            if abs(dx) + abs(dy) > 0:
                cand = our_dist[ny][nx]
                nd1 = cand + max(0, d1 - our_dist[sy][sx])  # keep deterministic, lightweight correction
            lead_now = d2 - d1
            lead_after = d2 - nd1
            # reward bigger positive lead; penalize negative lead
            sc += (lead_after * 2 + lead_now)
        # slight tie-break: stay away from obstacles by maximizing our local distance-to-frontier to reduce bad moves
        sc += -our_dist[ny][nx] * 0.01
        if sc > best_sc:
            best_sc = sc
            best = (dx, dy)

    return [best[0], best[1]]