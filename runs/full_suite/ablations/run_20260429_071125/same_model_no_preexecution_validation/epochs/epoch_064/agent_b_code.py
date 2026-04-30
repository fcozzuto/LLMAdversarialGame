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

    dself = bfs(sx, sy)
    doppo = bfs(ox, oy)
    legal = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            legal.append((dx, dy, nx, ny))

    if not legal:
        return [0, 0]

    # Score: best achievable "lead" over opponent for any resource, then prefer closeness.
    # If no winnable resources, move to reduce opponent lead (or just approach nearest resource).
    def eval_cell(x, y):
        best_lead = -INF
        best_dist = INF
        closest_res_dist = INF
        closest_margin = -INF
        for rx, ry in resources:
            ds = dself[rx][ry]
            do = doppo[rx][ry]
            if ds >= INF or do >= INF:
                continue
            # lead: positive means we can reach earlier (or same step with tiebreak via ds)
            lead = (do - ds)
            if lead > best_lead:
                best_lead = lead
            if lead == best_lead and ds < best_dist:
                best_dist = ds
            # from candidate cell, estimate we can reach quickly if we head there now
            ds2 = abs(rx - x) + abs(ry - y)  # quick deterministic proxy
            if ds2 < closest_res_dist:
                closest_res_dist = ds2
                closest_margin = lead
        if best_lead > 0:
            return (best_lead * 1000 - best_dist, -closest_res_dist, x - y)
        # No clear lead: try to reduce opponent advantage by going toward resource with smallest (do-ds)
        # or otherwise just approach nearest resource.
        if closest_res_dist < INF:
            # lower do-ds is better for blocking; use negative so higher is better
            return (-closest_margin * 1000 - closest_res_dist, closest_res_dist, x - y)
        return (-0, 0, x - y)

    best = None
    for dx, dy, nx, ny in legal:
        val = eval_cell(nx, ny)
        if best is None or val > best[0] or (val == best[0] and (dx, dy) < (best[1][0], best[1][1])):
            best = (val, (dx, dy))
    return [best[1][0], best[1][1]]