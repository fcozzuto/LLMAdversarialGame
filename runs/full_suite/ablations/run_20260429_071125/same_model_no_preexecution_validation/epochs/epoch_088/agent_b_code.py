def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources") or []
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

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
                    qx.append(nx)
                    qy.append(ny)
        return dist

    dS = bfs(sx, sy)
    dO = bfs(ox, oy)

    # Pick a target we can reach sooner; break ties by closeness to us and then by closeness to opponent
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
        # maximize: (we arrive earlier) and minimize our distance slightly
        key = (-(do - ds), -ds, do)  # deterministic total ordering
        if best is None or key > best_key:
            best = (rx, ry)
            best_key = key

    if best is None:
        # Fallback: move toward center while avoiding obstacles
        cx, cy = (w - 1) // 2, (h - 1) // 2
        bestm = (0, 0)
        bestd = INF
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            dd = abs(nx - cx) + abs(ny - cy)
            if dd < bestd:
                bestd = dd
                bestm = (dx, dy)
        return [int(bestm[0]), int(bestm[1])]

    tx, ty = best
    # Choose next step on our shortest path to target (greedy by dist)
    curd = dS[sx][sy]
    chosen = (0, 0)
    chosen_dist = curd
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = dS[nx][ny]
        if nd < chosen_dist or (nd == chosen_dist and (abs(nx - tx) + abs(ny - ty), abs(nx - ox) + abs(ny - oy)) <
                                 (abs((sx + chosen[0]) - tx) + abs((sy + chosen[1]) - ty),
                                  abs((sx + chosen[0]) - ox) + abs((sy + chosen[1]) - oy))):
            chosen_dist = nd
            chosen = (dx, dy)

    return [int(chosen[0]), int(chosen[1])]