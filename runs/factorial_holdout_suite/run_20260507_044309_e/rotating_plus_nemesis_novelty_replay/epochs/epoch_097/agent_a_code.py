def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources") or []
    obstacles_raw = observation.get("obstacles") or []
    obs = set(tuple(p) for p in obstacles_raw)
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def bfs_dist(start):
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        x0, y0 = start
        if not inb(x0, y0) or (x0, y0) in obs:
            return dist
        qx, qy, qi = [x0], [y0], 0
        dist[x0][y0] = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            d = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obs and d < dist[nx][ny]:
                    dist[nx][ny] = d
                    qx.append(nx)
                    qy.append(ny)
        return dist

    ds = bfs_dist((sx, sy))
    do = bfs_dist((ox, oy))

    best = None
    best_delta = -10**9
    best_sdist = 10**9
    best_pos = (10**9, 10**9)

    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in obs:
            continue
        d1 = ds[rx][ry]
        d2 = do[rx][ry]
        if d1 >= 10**9:
            continue
        delta = d2 - d1
        if delta > best_delta or (delta == best_delta and (d1 < best_sdist or (d1 == best_sdist and ((rx, ry) < best_pos)))):
            best_delta = delta
            best_sdist = d1
            best_pos = (rx, ry)
            best = (rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best

    curd = ds[sx][sy]
    best_m = (0, 0)
    best_nd = curd
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and (nx, ny) not in obs:
            nd = ds[nx][ny]
            if nd < best_nd or (nd == best_nd and (dx, dy) < best_m):
                best_nd = nd
                best_m = (dx, dy)

    return [int(best_m[0]), int(best_m[1])]