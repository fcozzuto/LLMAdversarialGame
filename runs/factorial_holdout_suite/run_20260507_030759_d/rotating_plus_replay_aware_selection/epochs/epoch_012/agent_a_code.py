def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation["resources"]
    obstacles = set(tuple(p) for p in observation["obstacles"])

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def bfs_from(start):
        inf = 10**9
        dist = [[inf] * h for _ in range(w)]
        x0, y0 = start
        if not inb(x0, y0):
            return dist
        qx = [x0]
        qy = [y0]
        dist[x0][y0] = 0
        qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            d = dist[x][y] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and dist[nx][ny] > d:
                    dist[nx][ny] = d
                    qx.append(nx)
                    qy.append(ny)
        return dist

    opp_dist = bfs_from((ox, oy))

    best = (0, 0)
    best_score = -10**18

    # deterministic tie-breaker: prefer smaller dx then dy (fixed moves order already)
    for mx, my in moves:
        nx, ny = sx + mx, sy + my
        if not inb(nx, ny):
            continue
        self_dist = bfs_from((nx, ny))
        move_score = -10**18
        for rx, ry in resources:
            ds = self_dist[rx][ry]
            do = opp_dist[rx][ry]
            if ds >= 10**8:
                continue
            # Immediate collection is huge.
            collect = 4000 if (ds == 0) else 0
            # Prefer resources where we arrive earlier; still pursue if we can't win.
            win = (do - ds)
            # Encourage shorter actual travel.
            s = collect + 50 * win - 3 * ds
            # Slightly prefer clearing nearer resources deterministically.
            s += 0.01 * (w - rx) + 0.001 * (h - ry)
            if s > move_score:
                move_score = s
        if move_score > best_score:
            best_score = move_score
            best = (mx, my)

    return [int(best[0]), int(best[1])]