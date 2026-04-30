def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
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

    opp_dist = bfs(ox, oy)
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best = (-INF, -INF)  # (primary score, secondary tiebreak)
    best_move = [0, 0]

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        sd = bfs(nx, ny)
        any_lead = False
        lead_score = -INF
        close_score = -INF
        for rx, ry in resources:
            d_s = sd[rx][ry]
            d_o = opp_dist[rx][ry]
            if d_s >= INF or d_o >= INF:
                continue
            adv = d_o - d_s  # positive means we arrive earlier
            if adv > 0:
                any_lead = True
                if adv > lead_score: lead_score = adv
            if -d_s > close_score: close_score = -d_s
        if any_lead:
            primary = 1000 + lead_score  # prefer any achievable lead
        else:
            primary = close_score  # race when no leads exist
        secondary = -(((nx - cx) * (nx - cx)) + ((ny - cy) * (ny - cy)))  # toward center deterministically
        if primary > best[0] or (primary == best[0] and secondary > best[1]):
            best = (primary, secondary)
            best_move = [dx, dy]

    return [int(best_move[0]), int(best_move[1])]