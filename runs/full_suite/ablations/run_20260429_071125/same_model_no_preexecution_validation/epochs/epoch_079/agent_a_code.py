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

    def best_target():
        best = None
        best_key = None
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            if not valid(rx, ry):
                continue
            ds = dS[rx][ry]
            if ds >= INF:
                continue
            do = dO[rx][ry]
            if do >= INF:
                do = INF
            gap = do - ds  # positive => we are closer
            val = gap * 10 - ds  # maximize: deny + get it fast
            key = (val, -ds, -ry, -rx)  # deterministic tie-break
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry, ds, do)
        return best

    target = best_target()
    if target is None:
        # fallback: go toward grid center while avoiding obstacles
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best_move = (0, 0)
        best_dist = INF
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            md = abs(nx - tx) + abs(ny - ty)
            if md < best_dist or (md == best_dist and (dx, dy) < best_move):
                best_dist = md
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    rx, ry, _, _ = target
    best = (0, 0)
    best_score = -INF
    # Prefer moves that reduce our distance to target, and (secondarily) increase our lead
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if