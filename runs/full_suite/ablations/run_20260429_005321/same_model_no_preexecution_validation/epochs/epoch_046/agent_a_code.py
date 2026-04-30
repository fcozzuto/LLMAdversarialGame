def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x,y): return 0 <= x < w and 0 <= y < h
    def blocked(x,y): return (x,y) in obstacles or not inb(x,y)

    if any(rx == sx and ry == sy for rx, ry in resources):
        return [0, 0]
    if not resources:
        return [0, 0]

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

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))
    if myd is None or opd is None:
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in resources:
        d1 = myd[ry][rx]; d2 = opd[ry][rx]
        if d1 >= INF or d2 >= INF:
            continue
        # Prefer targets I can reach earlier; if not, prefer minimizing my disadvantage.
        key = (d1 - d2, d1, -d2, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    if best is None:
        return [0, 0]

    tx, ty = best
    curd = myd[sy][sx]
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny): 
            continue
        nd = myd[ny][nx]
        od = opd[ny][nx]  # opponent distance to this cell not meaningful; ignore if INF
        candidates.append((nd, -opd[ty][tx] if opd[ty][tx] < INF else 0, -abs((opd[oy][ox] if opd else INF) - opd[ny][nx]), dx, dy))
    # Choose move that decreases my distance to target; tie-break by keeping opponent farther from target.
    bestm = None; bestk = None
    opp_target_dist = opd[ty][tx]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny): 
            continue
        my_to_t = myd[ny][tx]
        if my_to_t >= INF:
            continue
        k = (my_to_t, -opp_target_dist, abs((my_to_t - curd)), dx, dy)
        if bestk is None or k < bestk:
            bestk = k
            bestm = (dx, dy)
    if bestm is None:
        return [0, 0]
    return [int(bestm[0]), int(bestm[1])]