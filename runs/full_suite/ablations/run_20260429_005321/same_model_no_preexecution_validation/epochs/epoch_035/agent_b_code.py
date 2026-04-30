def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def bfs(start, limit=63):
        if not inb(start[0], start[1]) or start in obstacles: return None
        INF = 10**9
        dist = [[INF]*w for _ in range(h)]
        x0, y0 = start
        dist[y0][x0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]; qi += 1
            d = dist[y][x]
            if d >= limit: 
                continue
            nd = d + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx); qy.append(ny)
        return dist
    def best_step_toward(target, myd):
        tx, ty = target
        best = (0, 0, myd[ty][tx] if inb(tx, ty) else 10**9)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles: 
                continue
            dnext = myd[ny][nx]
            if dnext < best[2] or (dnext == best[2] and (dx, dy) < (best[0], best[1])):
                best = (dx, dy, dnext)
        return [best[0], best[1]]
    if not resources:
        return [0, 0]
    myd = bfs((sx, sy)); opd = bfs((ox, oy))
    if myd is None or opd is None:
        # deterministic fallback: move toward board center
        cx, cy = (w-1)/2.0, (h-1)/2.0
        dx = -1 if sx > cx else (1 if sx < cx else 0)
        dy = -1 if sy > cy else (1 if sy < cy else 0)
        return [dx, dy]
    # Choose resource where we arrive earlier; break ties by distance advantage then lexicographic
    candidates = []
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in obstacles: 
            continue
        dm = myd[ry][rx]; do = opd[ry][rx]
        if dm >= 10**8: 
            continue
        rel = do - dm  # positive: we are earlier
        key = (-rel, dm, (rx, ry))
        candidates.append((key, (rx, ry)))
    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: t[0])
    tx, ty = candidates[0][1]
    return best_step_toward((tx, ty), myd)