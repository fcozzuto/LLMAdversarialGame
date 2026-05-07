def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def passable(x, y): return inb(x, y) and (x, y) not in obstacles
    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    if any((rx == sx and ry == sy) for rx, ry in resources):
        return [0, 0]
    dirs = cand[:]
    def bfs(start):
        x0, y0 = start
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        if not passable(x0, y0):
            return dist
        dist[x0][y0] = 0
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            d = dist[x][y] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if passable(nx, ny) and dist[nx][ny] > d:
                    dist[nx][ny] = d
                    q.append((nx, ny))
        return dist
    ds = bfs((sx, sy))
    do = bfs((ox, oy))
    INF = 10**9
    best = None
    for rx, ry in resources:
        sd, od = ds[rx][ry], do[rx][ry]
        if sd >= INF: 
            continue
        adv = od - sd
        key = (adv, -sd, -od)
        if best is None or key > best[0]:
            best = (key, (rx, ry), sd)
    if best is None:
        # fallback: move to reduce manhattan to nearest reachable resource
        if not resources:
            return [0, 0]
        target = min(resources, key=lambda r: abs(r[0]-sx) + abs(r[1]-sy))
    else:
        target = best[1]
    tx, ty = target
    best_move = (None, -INF)
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not passable(nx, ny):
            continue
        nd = ds[nx][ny]
        if nd >= INF:
            continue
        adv = do[tx][ty] - nd
        score = (adv, -nd, -abs(nx - tx) - abs(ny - ty))
        if best_move[0] is None or score > best_move[1]:
            best_move = ((dx, dy), score)
    if best_move[0] is None:
        return [0, 0]
    return [int(best_move[0][0]), int(best_move[0][1])]