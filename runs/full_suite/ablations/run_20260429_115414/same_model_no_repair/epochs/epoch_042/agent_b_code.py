def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    INF = 10**9

    def bfs(start):
        dist = [[INF] * h for _ in range(w)]
        x0, y0 = start
        if not inb(x0, y0):
            return dist
        dist[x0][y0] = 0
        qx, qy = [x0], [y0]
        i = 0
        while i < len(qx):
            x, y = qx[i], qy[i]
            i += 1
            nd = dist[x][y] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx)
                    qy.append(ny)
        return dist

    if not resources:
        return [0, 0]

    ds = bfs((sx, sy))
    do = bfs((ox, oy))

    best = None
    best_key = None
    for rx, ry in resources:
        if not inb(rx, ry):
            continue
        d1 = ds[rx][ry]
        if d1 >= INF:
            continue
        d2 = do[rx][ry]
        if d2 >= INF:
            d2 = INF
        val = d1 - d2  # smaller means I'm relatively closer
        key = (val, d1, -rx, -ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]

    tx, ty = best
    best_move = (0, 0)
    best_dist = ds[sx][sy]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and ds[nx][ny] < best_dist:
            best_dist = ds[nx][ny]
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]