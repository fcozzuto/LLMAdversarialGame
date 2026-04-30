def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (not inb(x, y)) or ((x, y) in obstacles)

    INF = 10**9
    def bfs(start):
        x0, y0 = start
        if blocked(x0, y0): return None
        dist = [[INF] * w for _ in range(h)]
        dist[y0][x0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if not blocked(nx, ny) and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    if not resources:
        return [0, 0]

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))
    if myd is None or opd is None:
        return [0, 0]

    # Choose resource where we are closer than opponent; otherwise fallback to nearest we can reach.
    best = None
    best_val = -10**18
    for rx, ry in resources:
        d1 = myd[ry][rx]; d2 = opd[ry][rx]
        if d1 >= INF: 
            continue
        # Prefer winning races (d1 small, d2 large), but also avoid extreme delays.
        val = (d2 - d1) * 1000 - d1 * 3
        # Small deterministic bias to keep movement varied:
        val += (rx * 11 + ry * 7) * 1e-6
        if val > best_val:
            best_val = val
            best = (rx, ry)

    if best is None:
        # No reachable resource: move toward center.
        tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
        cx = 0; cy = 0
        best_step = (0, 0)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if blocked(nx, ny): 
                continue
            score = -((nx - tx) ** 2 + (ny - ty) ** 2)
            if score > cx:
                cx = score; best_step = (dx, dy)
        return [best_step[0], best_step[1]]

    tx, ty = best
    cur = myd[sy][sx]
    # If already on target, step to improve future position: go to any resource-adjacent shortest neighbor.
    if sx == tx and sy == ty:
        # Deterministically try to move to reduce distance to the next best resource (or center).
        next_best = None; next_val = -10**18
        for rx, ry in resources:
            if (rx, ry) == (tx, ty): 
                continue
            d1 = myd[ry][rx]; d2 = opd[ry][rx]
            if d1 >= INF: 
                continue
            val = (d2 - d1) * 1000 - d1 * 3 + (rx * 11 + ry * 7) * 1e-6
            if val > next_val:
                next_val = val; next_best = (rx, ry)
        if next_best is None:
            tx, ty = (w - 1) / 2.0, (h - 1) / 2.0
            best_step = (0, 0); best_sc = -10**18
            for dx, dy in dirs:
                nx, ny = sx + dx, sy + dy
                if blocked(nx, ny): 
                    continue
                sc = -((nx - tx) ** 2 + (ny - ty) ** 2)
                if sc > best_sc:
                    best_sc = sc