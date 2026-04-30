def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    INF = 10**9

    def bfs(start):
        x0, y0 = start
        dist = [[INF]*w for _ in range(h)]
        if not inb(x0, y0) or (x0, y0) in obstacles:
            return dist
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

    def choose_target():
        best = None; best_key = None
        any_valid = False
        for rx, ry in resources:
            md = myd[ry][rx]; od = opd[ry][rx]
            if md >= INF or (rx, ry) in obstacles:
                continue
            any_valid = True
            # Key favors resources we can reach earlier, then far advantage, then shorter time.
            key = (-(od - md), md, -(od), rx + ry)
            # We want smallest "time advantage cost": larger (od-md) => smaller -(od-md)
            # Thus key above works with lexicographic minimization.
            if best_key is None or key < best_key:
                best_key = key; best = (rx, ry)
        if any_valid:
            return best
        # No reachable resources: go toward center.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        return (cx, cy)

    tx, ty = choose_target()
    # If center is blocked, fallback to any reachable cell near center.
    if (tx, ty) in obstacles or myd[ty][tx] >= INF:
        # Pick nearest reachable among up to 9 central candidates.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        candidates = [(cx + dx, cy + dy) for dx in (-1,0,1) for dy in (-1,0,1)]
        best = (sx, sy); bd = myd[sy][sx]
        for x, y in candidates:
            if inb(x, y) and (x, y) not in obstacles and myd[y][x] < bd:
                bd = myd[y][x]; best = (x, y)
        tx, ty = best

    # Choose move that minimizes our distance to target, while maximizing opponent disadvantage.
    best_move = (0, 0); best_tuple = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        md_next = myd[ny][tx]
        # Opponent disadvantage: if opponent can also reach target quickly, discourage.
        od_t = opd[ty][tx]
        # Also slightly discourage letting opponent land nearer to our next position.
        opp_to_next = opd[ny][sx] if inb(sx, sx) else INF  # harmless, keeps deterministic
        key = (md_next, (od_t - myd[ny][tx]), -(myd[ny][tx] - myd[sy][tx]), dx*dx +