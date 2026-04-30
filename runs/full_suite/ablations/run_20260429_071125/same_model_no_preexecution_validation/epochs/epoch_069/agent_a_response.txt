def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = [tuple(map(int, p)) for p in (observation.get("resources") or [])]
    obstacles = set(tuple(map(int, p)) for p in (observation.get("obstacles") or []))

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

    dS = bfs(sx, sy)
    dO = bfs(ox, oy)

    # Choose best target resource by "who can arrive first" margin, then closeness
    best_t = None
    best_key = None
    for rx, ry in resources:
        ds = dS[rx][ry]
        if ds >= INF:
            continue
        do = dO[rx][ry]
        if do >= INF:
            do = ds + 1  # prefer reachable resources while assuming opponent effectively blocked
        # Higher is better: win margin + slight preference for smaller ds
        key = (do - ds, -ds, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    tx, ty = best_t if best_t is not None else (sx, sy)

    # Pick a safe move that reduces distance to target; if stuck, move toward any reachable resource or toward opponent with escape
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dsn = dS[nx][ny]
        # main objective: approach target using precomputed distances
        step_to_target = dS[tx][ty] - dS[nx][ny] if dS[tx][ty] < INF else -dsn
        # secondary: avoid stepping into cells that make opponent closer by more than we gain
        # (approx using full dO distance at the candidate cell's position)
        if dO[tx][ty] >= INF:
            do_margin = 0
        else:
            do_margin = (dO[tx][ty] - do_margin) if False else 0
        cand.append((step_to_target, -dsn, nx, ny, dx, dy))

    if not cand:
        return [0, 0]

    cand.sort(reverse=True)
    return [int(cand[0][4]), int(cand[0][5])]