def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation.get("grid_width", 8), observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = set((p[0], p[1]) for p in obstacles if isinstance(p, (list, tuple)) and len(p) == 2)

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def bfs_dist(start):
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        x0, y0 = start
        if not inb(x0, y0) or (x0, y0) in blocked:
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
                if inb(nx, ny) and (nx, ny) not in blocked and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    if (sx, sy) in blocked:
        for dx, dy in [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in blocked:
                return [dx, dy]
        return [0, 0]

    if not resources:
        # Deterministic fallback: drift to nearest corner away from opponent
        corners = [(0, 0), (0, h - 1), (w - 1, 0), (w - 1, h - 1)]
        cx, cy = max(corners, key=lambda c: abs(c[0] - ox) + abs(c[1] - oy))
        dx = 0 if cx == sx else (1 if cx > sx else -1)
        dy = 0 if cy == sy else (1 if cy > sy else -1)
        return [dx, dy]

    sd = bfs_dist((sx, sy))
    od = bfs_dist((ox, oy))

    best = None
    # Score: prioritize resources we can reach earlier; punish those opponent can reach sooner.
    for rx, ry in resources:
        ds = sd[rx][ry]
        do = od[rx][ry]
        if ds >= 10**9:
            continue
        if do >= 10**9:
            do = ds + 5  # treat unreachable for opponent as favorable
        score = (do - ds) * 100 - ds
        # Deterministic tie-break by coord
        key = (-score, ds, rx, ry)
        if best is None or key < best[0]:
            best = (key, (rx, ry))

    if best is None:
        return [0, 0]

    tx, ty = best[1]
    # Choose a move that reduces our distance to the target
    cur = sd[sx][sy]
    best_move = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in blocked:
            continue
        nd = sd[nx][ny]
        # Prefer strict improvement; otherwise minimal distance; deterministic coord tie.
        if nd < cur:
            k = (0, nd, abs(nx - tx) + abs(ny - ty), dx, dy)
        else:
            k = (1, nd, abs(nx - tx) + abs(ny - ty), dx, dy)
        if best_key is None or k < best_key:
            best_key = k
            best_move = (dx, dy)
    if best_move is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]