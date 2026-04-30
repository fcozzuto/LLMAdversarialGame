def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (not inb(x, y)) or ((x, y) in obstacles)

    def bfs(start):
        x0, y0 = start
        if blocked(x0, y0): return None
        INF = 10**9
        dist = [[INF] * w for _ in range(h)]
        dist[y0][x0] = 0
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if not blocked(nx, ny) and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    q.append((nx, ny))
        return dist

    if not resources:
        return [0, 0]

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))
    if myd is None or opd is None:
        return [0, 0]

    res_set = set((r[0], r[1]) for r in resources)
    if (sx, sy) in res_set:
        return [0, 0]

    best_r = None
    best_score = -10**18
    best_mdist = 10**18
    INF = 10**9

    for rx, ry in resources:
        m = myd[ry][rx]; o = opd[ry][rx]
        if m >= INF or o >= INF:
            continue
        score = (o - m) * 1000 - m  # primary: win margin; secondary: faster
        if score > best_score or (score == best_score and m < best_mdist):
            best_score = score
            best_mdist = m
            best_r = (rx, ry)

    if best_r is None:
        return [0, 0]

    tx, ty = best_r
    cur_d = myd[sy][sx]
    if cur_d == 0:
        return [0, 0]

    best_move = (0, 0)
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        nm = myd[ny][nx]
        if nm >= INF:
            continue
        # prefer getting closer to target and improving my lead over opponent
        no = opd[ny][nx]
        val = (opd[ty][tx] - nm) * 1000 - nm
        if (opd[ny][nx] < opd[sy][sx]):  # opportunistic blocking of opponent-front
            val += 50
        if nm < cur_d or val > best_val or (val == best_val and (dx, dy) < best_move):
            best_val = val
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]