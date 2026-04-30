def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    obstacles = {(int(p[0]), int(p[1])) for p in (observation.get("obstacles") or [])}
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    INF = 10**9

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def free(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not free(x0, y0):
            return dist
        dist[x0][y0] = 0
        qx, qy, qi = [x0], [y0], 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if free(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx)
                    qy.append(ny)
        return dist

    myd = bfs(sx, sy)
    opd = bfs(ox, oy)

    best = None
    best_score = -10**18
    for rx, ry in resources:
        dm = myd[rx][ry]
        if dm >= INF:
            continue
        do = opd[rx][ry]
        do_val = do if do < INF else 10**6
        score = (do_val - dm) * 1000 - dm  # prefer resources we can beat, then closer
        if score > best_score:
            best_score = score
            best = (rx, ry)

    cx, cy = sx, sy
    tx, ty = best if best is not None else (w // 2, h // 2)

    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if free(nx, ny):
            candidates.append((dx, dy, myd[nx][ny], (nx, ny)))

    if not candidates:
        return [0, 0]

    if best is not None:
        txd = myd[tx][ty]
        # Choose move that most decreases distance to the target (ties by dx,dy ordering)
        candidates.sort(key=lambda t: (abs(t[3][0] - tx) + abs(t[3][1] - ty), t[2], t[0], t[1]))
        # Prefer stepping to a cell with strictly smaller distance if possible
        curd = myd[sx][sy]
        better = [c for c in candidates if c[2] < curd]
        pool = better if better else candidates
        best_move = min(pool, key=lambda c: (abs(c[3][0] - tx) + abs(c[3][1] - ty), c[2], c[0], c[1]))
        return [int(best_move[0]), int(best_move[1])]

    # No reachable resources: drift toward center with safety
    cx, cy = w // 2, h // 2
    best_move = min(candidates, key=lambda c: (abs(c[3][0] - cx) + abs(c[3][1] - cy), c[0], c[1]))
    return [int(best_move[0]), int(best_move[1])]