def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def bfs(start):
        x0, y0 = start
        dist = [[INF] * w for _ in range(h)]
        if not inb(x0, y0) or (x0, y0) in obstacles:
            return dist
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

    best_r = None
    best_key = (-INF, INF)  # (win_margin, -dm) with deterministic ordering
    for rx, ry in resources:
        dm = myd[ry][rx]; do = opd[ry][rx]
        if dm >= INF or do >= INF:
            continue
        win_margin = do - dm  # >0 means we arrive earlier
        key = (win_margin, -dm)
        if win_margin > 0:
            if key[0] > best_key[0] or (key[0] == best_key[0] and key[1] > best_key[1]):
                best_key = key; best_r = (rx, ry)

    if best_r is None:
        # If no "guaranteed" earlier resource, contest the most valuable race: opponent-near, we closest.
        best_r = None
        best_key = (-INF, INF, INF)  # (-do, dm, rx+ry)
        for rx, ry in resources:
            dm = myd[ry][rx]; do = opd[ry][rx]
            if dm >= INF or do >= INF:
                continue
            key = (-do, dm, rx + ry)
            if best_r is None or key < best_key:
                best_key = key; best_r = (rx, ry)

    tr, ty = best_r if best_r is not None else