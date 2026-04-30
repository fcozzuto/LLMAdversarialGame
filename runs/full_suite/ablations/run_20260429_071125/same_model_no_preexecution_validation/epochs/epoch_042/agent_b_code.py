def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
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

    if not resources:
        return [0, 0]

    distS = bfs(sx, sy)
    distO = bfs(ox, oy)

    best_r = None
    best_adv = -INF
    for rx, ry in resources:
        ds = distS[rx][ry]
        do = distO[rx][ry]
        if ds >= INF or do >= INF:
            continue
        adv = do - ds  # positive means I'm closer
        if adv > best_adv:
            best_adv = adv
            best_r = (rx, ry)

    if best_r is None:
        # fallback: move to any reachable resource-closer cell
        reachable_best = (None, -INF)
        for mx, my in moves:
            nx, ny = sx + mx, sy + my
            if not valid(nx, ny):
                continue
            best_d = min(distS[rx][ry] for rx, ry in resources if distS[rx][ry] < INF)
            if best_d > -INF:
                reachable_best = ((nx, ny), -best_d)
                break
        if reachable_best[0] is None:
            return [0, 0]
        tx, ty = reachable_best[0]
        return [tx - sx, ty - sy]

    rx, ry = best_r
    # choose move that maximizes (opponent disadvantage) and minimizes my distance to target
    best_move = (0, 0)
    best_val = -INF
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        myd = distS[nx][ny]
        # If already at target, hold position to secure it.
        if (nx, ny) == (rx, ry):
            return [dx, dy]
        # approximate advantage at new position relative to target
        target_my = distS[nx][ny] + (0 if (nx, ny) == (rx, ry) else distS[rx][ry] - distS[sx][sy] if distS[sx][sy] < INF else 0)
        target_my = myd + max(0, distS[rx][ry] - distS[sx][sy])  # monotone-ish
        target_op