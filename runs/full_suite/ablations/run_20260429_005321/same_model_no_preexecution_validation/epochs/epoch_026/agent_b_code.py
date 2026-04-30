def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = {(p[0], p[1]) for p in obstacles_list}

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def bfs(start):
        x0, y0 = start
        if not inb(x0, y0) or (x0, y0) in obstacles:
            return None
        dist = [[INF] * w for _ in range(h)]
        dist[y0][x0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))

    target = None
    if resources and myd is not None and opd is not None:
        best = None  # (advantage, -do, dm, tie_x, tie_y)
        for rx, ry in resources:
            dm = myd[ry][rx]; do = opd[ry][rx]
            if dm >= INF:
                continue
            if do >= INF:
                do = INF
            advantage = do - dm  # positive means we arrive earlier
            key = (advantage, -do, dm, rx, ry)
            if best is None or key > best:
                best = key
                target = (rx, ry)

    if target is None:
        target = (ox, oy)

    tx, ty = target
    # Greedy step toward target with obstacle safety; deterministic tie-break by dir order.