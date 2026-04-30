def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0):
            return dist
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

    best = None
    best_margin = -10**18
    best_ds = INF
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not valid(rx, ry):
            continue
        ds = dS[rx][ry]
        do = dO[rx][ry]
        if ds >= INF:
            continue
        margin = do - ds  # positive means we arrive earlier
        if margin > best_margin or (margin == best_margin and ds < best_ds):
            best_margin = margin
            best_ds = ds
            best = (rx, ry)

    if best is None:
        # If no reachable resources, move to best improvement in our distance to opponent's position.
        target = (ox, oy)
    else:
        target = best

    tx, ty = target
    curd = dS[sx][sy]
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            candidates.append((dS[nx][ny], nx, ny, dx, dy))
    if not candidates:
        return [0, 0]
    # Prefer reducing our distance to target; break ties toward center-ish and toward opponent if still tied.
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    def score(item):
        dist, nx, ny, dx, dy = item
        tie = abs(dist - min(c[0] for c in candidates)) < 1e-9
        # secondary: closer to target, then closer to center, then closer to opponent
        return (dist, (abs(nx - tx) + abs(ny - ty)), (abs(nx - cx) + abs(ny - cy)), (abs(nx - ox) + abs(ny - oy)))
    best_item = min(candidates, key=score)
    return [int(best_item[3]), int(best_item[4])]