def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    INF = 10**9

    def bfs(start):
        x0, y0 = start
        if not inb(x0, y0) or (x0, y0) in obstacles: return None
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

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))
    if myd is None or opd is None:
        return [0, 0]

    best = None
    best_val = -10**18
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in obstacles:
            continue
        md = myd[ry][rx]; od = opd[ry][rx]
        if md >= INF or od >= INF:
            continue
        # Prefer winning the race; otherwise prefer largest relative advantage, then closest.
        val = (od - md) * 1000 - md
        if val > best_val:
            best_val = val; best = (rx, ry)

    if best is None:
        # Deterministic fallback: move toward closest reachable resource.
        best = None; bestd = INF
        for rx, ry in resources:
            if inb(rx, ry) and (rx, ry) not in obstacles and myd[ry][rx] < bestd:
                bestd = myd[ry][rx]; best = (rx, ry)
        if best is None:
            return [0, 0]

    tx, ty = best
    curd = myd[sy][sx]
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        # Choose move that reduces distance to target; break ties by blocking opponent path (increase their distance to target).
        mdn = myd[ny][nx]; odn = opd[ty][tx]  # constant, kept for clarity
        score = (curd - mdn) * 1000 + (opd[ty][tx] - opd[ny][tx]) if opd[ny][tx] < INF else (curd - mdn) * 1000
        if score > best_score:
            best_score = score; best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]