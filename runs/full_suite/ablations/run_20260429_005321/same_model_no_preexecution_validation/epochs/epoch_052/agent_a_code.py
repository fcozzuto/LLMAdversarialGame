def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs = set(tuple(p) for p in (observation.get("obstacles") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (not inb(x, y)) or ((x, y) in obs)

    if not resources: return [0, 0]
    if blocked(sx, sy) or blocked(ox, oy): return [0, 0]
    res_set = set(tuple(r) for r in resources)
    if (sx, sy) in res_set: return [0, 0]

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

    myd = bfs((sx, sy)); opd = bfs((ox, oy))
    if myd is None or opd is None: return [0, 0]

    best = None; best_key = None
    for rx, ry in resources:
        md = myd[ry][rx]; od = opd[ry][rx]
        if md >= INF or od >= INF: 
            continue
        # Primary: maximize advantage (opponent further than us)
        # Secondary: finish sooner
        # Tertiary: break ties deterministically by coordinates
        key = (od - md, -md, -(rx + 7 * ry), rx, ry)
        if best_key is None or key > best_key:
            best_key = key; best = (rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best

    # Choose the move that minimizes our distance to target; avoid obstacles.
    curd = myd[sy][sx]
    bestm = (0, 0); bestv = curd + 10**6
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny): 
            continue
        v = myd[ny][nx]
        if v < bestv:
            bestv = v; bestm = (dx, dy)
        elif v == bestv:
            # tie-break: move that also reduces opponent's best reachable dist to target (mild blocking)
            ov = opd[ny][nx] if opd else INF
            if ov < opd[sy][sx]:
                bestm = (dx, dy)

    return [bestm[0], bestm[1]]