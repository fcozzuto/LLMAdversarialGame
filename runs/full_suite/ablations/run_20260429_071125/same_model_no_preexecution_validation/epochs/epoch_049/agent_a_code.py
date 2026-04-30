def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation["self_position"])
    ox, oy = map(int, observation["opponent_position"])
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

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

    distS = bfs(sx, sy)
    distO = bfs(ox, oy)

    best = None
    best_key = None
    for tx, ty in resources:
        ds = distS[tx][ty]
        if ds >= INF:
            continue
        do = distO[tx][ty]
        if do >= INF:
            key = (-1, ds, tx, ty)  # prioritize reachable when opponent can't
        else:
            adv = do - ds  # positive => we arrive first
            key = (0 if adv < 0 else 1, -adv, ds, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best = (tx, ty)

    if best is None:
        return [0, 0]

    tx, ty = best
    best_step = (0, 0)
    best_d = distS[sx][sy]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny) and distS[nx][ny] < best_d:
            best_d = distS[nx][ny]
            best_step = (dx, dy)

    # If no strictly decreasing step (stuck by obstacles), choose step that reduces ds the most, tie by dx/dy order.
    if best_step == (0, 0):
        cur = distS[sx][sy]
        cand = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                d = distS[nx][ny]
                if d < cur:
                    k = (d, dx, dy)
                    if cand is None or k < cand[0]:
                        cand = (k, (dx, dy))
        if cand is not None:
            best_step = cand[1]

    return [int(best_step[0]), int(best_step[1])]