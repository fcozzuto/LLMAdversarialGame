def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    INF = 10**9

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

    # If no reachable resources, drift toward center unless blocked by obstacle.
    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (10**9, None)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                d = abs(nx - cx) + abs(ny - cy)
                if d < best[0]: best = (d, (dx, dy))
        return best[1] if best[1] is not None else [0, 0]

    # Choose resource by maximizing lead: (opponent_dist - my_dist), then prefer smaller my_dist, then stable tie.
    best = None
    best_tuple = (-10**18, -10**18, 10**18, 10**18)
    for rx, ry in resources:
        if (rx, ry) in obstacles: 
            continue
        md = myd[ry][rx]
        if md >= INF:
            continue
        od = opd[ry][rx]
        if od >= INF:
            od = INF
        lead = od - md
        key = (lead, -md, rx, ry)
        if best is None or key > best_tuple:
            best_tuple = key
            best = (rx, ry)
    if best is None:
        # Same fallback as above
        cx, cy = (w - 1) // 2, (h - 1) // 2
        bestm = (10**9, None)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                d = abs(nx - cx) + abs(ny - cy)
                if d < bestm[0]: bestm = (d, (dx, dy))
        return bestm[1] if bestm[1] is not None else [0, 0]

    tx, ty = best

    # Choose next step greedily toward target along shortest myd; break ties by improving opponent disadvantage.
    best_score = (-10**18, -10**18, 10**18)
    best_move = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        md_next = myd[ny][nx]
        # prefer cells from which target is reachable and closer
        if md_next >= INF:
            continue
        # The actual distance-to-target heuristic uses myd at target: md_curr -