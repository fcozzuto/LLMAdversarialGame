def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def bfs(start):
        x0, y0 = start
        if not inb(x0, y0) or (x0, y0) in obstacles:
            return None
        dist = [[INF]*w for _ in range(h)]
        dist[y0][x0] = 0
        q = [(x0, y0)]; qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    q.append((nx, ny))
        return dist

    if not resources:
        return [0, 0]

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))
    if myd is None or opd is None:
        return [0, 0]

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    best = None  # (score, dm, -rx, -ry)
    for rx, ry in resources:
        dm = myd[ry][rx]; do = opd[ry][rx]
        if dm >= INF and do >= INF:
            continue
        # Prefer resources we can reach and the opponent can't (or is slower).
        score = (do - dm)
        if dm >= INF:
            score -= 10000
        # Slight preference for earlier and more central.
        score += -0.05 * dm + -0.01 * (abs(rx - cx) + abs(ry - cy))
        key = (score, dm, -rx, -ry)
        if best is None or key > best[0:4]:
            best = key

    if best is None:
        return [0, 0]

    _, target_dm, _, _ = best
    # Recover target by scanning best-scored again deterministically
    best_t = resources[0]
    best_key = (-INF, INF, 0, 0)
    for rx, ry in resources:
        dm = myd[ry][rx]; do = opd[ry][rx]
        if dm >= INF and do >= INF:
            continue
        score = (do - dm)
        if dm >= INF:
            score -= 10000
        score += -0.05 * dm + -0.01 * (abs(rx - cx) + abs(ry - cy))
        key = (score, dm, -rx, -ry)
        if key > best_key:
            best_key = key; best_t = (rx, ry)

    tx, ty = best_t
    # Choose move minimizing our distance to target; if tied, minimize opponent distance.
    cur_dm = myd[sy][sx]
    best_mv = (INF, INF, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy; dx, dy = 0, 0
        d1 = myd[ny][nx] if myd[ny][nx] < INF else INF
        d2 = opd[ny][nx] if opd[ny][nx] < INF else INF
        # Deterministic tie-break: also prefer moves that reduce our distance.
        dec = 0 if d1 >= cur_dm else (cur_dm - d1)
        key = (d1, d2, -dec, dx*3 + dy)
        if key < best_mv:
            best_mv = key; best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]