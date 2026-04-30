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
        qx, qy = [x0], [y0]
        qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    dS = bfs(sx, sy)
    dO = bfs(ox, oy)

    if not resources:
        cx, cy = w // 2, h // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            md = abs(nx - cx) + abs(ny - cy)
            fo = abs(nx - ox) + abs(ny - oy)
            score = (-fo, md)  # maximize foe distance, then minimize center distance
            if best is None or score < best[0]:
                best = (score, (dx, dy))
        return best[1] if best else [0, 0]

    # Pick a resource where we have the largest (our_closeness - opponent_closeness) differential.
    best_r = None
    best_adv = -INF
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not inb(rx, ry) or (rx, ry) in obstacles:
            continue
        ds = dS[rx][ry]
        do = dO[rx][ry]
        if ds >= INF or do >= INF:
            continue
        adv = do - ds  # positive => we closer
        # Small deterministic bias toward upper-left (lexicographic) to break ties.
        if best_r is None or adv > best_adv or (adv == best_adv and (rx, ry) < best_r):
            best_adv = adv
            best_r = (rx, ry)

    # If all resources unreachable, revert to maximizing distance from opponent while moving toward center.
    if best_r is None:
        cx, cy = w // 2, h // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            foe = abs(nx - ox) + abs(ny - oy)
            cen = abs(nx - cx) + abs(ny - cy)
            score = (-foe, cen)
            if best is None or score < best[0]:
                best = (score, (dx, dy))
        return best[1] if best else [0, 0]

    tx, ty = best_r

    # Choose the move that improves our distance to the target; secondary: increases distance from opponent.
    best = None
    for dx, dy in moves:
        nx