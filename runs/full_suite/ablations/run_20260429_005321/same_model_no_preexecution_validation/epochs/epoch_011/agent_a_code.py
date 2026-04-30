def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    INF = 10**9
    def bfs(x0, y0):
        if not inb(x0, y0) or (x0, y0) in obstacles:
            return [[INF] * w for _ in range(h)]
        dist = [[INF] * w for _ in range(h)]
        dist[y0][x0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x = qx[qi]; y = qy[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    dist_s = bfs(sx, sy)
    dist_o = bfs(ox, oy)

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = (10**9, 10**9, None)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                val = abs(nx - tx) + abs(ny - ty)
                if (val, - (dist_o[ny][nx] if dist_o[ny][nx] < INF else -INF), dx, dy) < best:
                    best = (val, - (dist_o[ny][nx] if dist_o[ny][nx] < INF else -INF), dx, dy)
        return [best[2], best[3]] if best[2] is not None else [0, 0]

    best_res = None
    best_key = None
    for rx, ry in resources:
        ds = dist_s[ry][rx]; do = dist_o[ry][rx]
        if ds >= INF or do >= INF:
            continue
        # Prefer resources where opponent is farther; break ties by getting there sooner.
        key = (do - ds, -ds, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best_res = (rx, ry)

    if best_res is None:
        # Fallback: head toward any reachable resource by smallest ds
        target = None; tds = INF
        for rx, ry in resources:
            ds = dist_s[ry][rx]
            if ds < tds:
                tds = ds; target = (rx, ry)
        best_res = target if target is not None else (sx, sy)

    tx, ty = best_res
    best_move = (10**9, -10**9, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        ds2 = dist_s[ny][nx]
        if ds2 >= INF:
            continue
        # Primary: minimize distance to target; Secondary: maximize opponent