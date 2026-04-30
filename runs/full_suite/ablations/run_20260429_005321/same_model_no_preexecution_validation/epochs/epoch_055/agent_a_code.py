def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    inb = lambda x,y: 0 <= x < w and 0 <= y < h
    blocked = lambda x,y: (not inb(x,y)) or ((x,y) in obs)

    if blocked(sx, sy):
        return [0, 0]
    if not resources:
        return [0, 0]

    INF = 10**9
    def bfs(start):
        if blocked(start[0], start[1]): return None
        dist = [[INF]*w for _ in range(h)]
        dist[start[1]][start[0]] = 0
        qx = [start[0]]; qy = [start[1]]; qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if not blocked(nx, ny) and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))
    if myd is None:
        return [0, 0]
    if opd is None:
        opd = [[INF]*w for _ in range(h)]

    best = None
    best_key = None
    for rx, ry in resources:
        md = myd[ry][rx]
        if md >= INF: 
            continue
        od = opd[ry][rx]
        # Prefer positions where we can arrive strictly earlier; else nearest.
        if od < INF:
            ahead = (md < od)
            key = (0 if ahead else 1, md, -od, rx, ry)
        else:
            key = (0, md, 0, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]

    tx, ty = best
    curd = myd[sy][sx]
    # Choose next step that minimizes our BFS distance to the target; tie-break deterministically.
    best_move = [0, 0]
    best_dist = myd[sy][sx]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        d = myd[ny][nx]  # lower is closer to start; not what we want
        # Use target-distance as primary criterion: dist from neighbor to target via BFS from neighbor is expensive.
        # Instead, we use monotonic greedy: among neighbors, pick one with smaller (myd_to_target estimate)
        # Estimate via difference in BFS distance-to-start (works as consistent in unweighted graphs for shortest paths).
        # We want to reduce shortest-path distance to target: approximate by aiming for cells closer to target in geometry.
        # Robust proxy: reduce Euclidean squared distance to target first, then keep BFS-to-start monotone.
        g = (nx - tx) * (nx - tx) + (ny - ty) * (ny - ty)
        monot = abs((myd[ny][nx] - curd) - 1)  # prefer plausible progress
        cand = (g, monot, dx, dy)
        # We can also check exact target if neighbor lies on a shortest route: compare BFS-to-start levels only.
        # Primary objective: minimize geometric g; secondary: monotonic progress; tertiary: deterministic.
        if best_move == [0, 0]:
            best_score = cand
            best_move = [dx, dy]
            best_dist = g
        else:
            if cand < best_score:
                best_score = cand
                best_move = [dx, dy]

    # Ensure we don't move into obstacle (engine will keep in place anyway, but be safe)
    nx, ny = sx + best_move[0], sy + best_move[1]
    if blocked(nx, ny):