def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (not inb(x, y)) or ((x, y) in obs)

    if not resources: return [0, 0]
    if blocked(sx, sy) or blocked(ox, oy): return [0, 0]
    if any(r[0] == sx and r[1] == sy for r in resources): return [0, 0]

    INF = 10**9
    def bfs(start):
        x0, y0 = start
        if blocked(x0, y0): return None
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

    myd = bfs((sx, sy)); opd = bfs((ox, oy))
    if myd is None or opd is None: return [0, 0]

    best_res = None; best_key = None
    for rx, ry in resources:
        md = myd[ry][rx]; od = opd[ry][rx]
        if md >= INF or od >= INF: 
            continue
        key = (od - md, -md, -(rx + ry), rx, ry)
        if best_key is None or key > best_key:
            best_key = key; best_res = (rx, ry)
    if best_res is None:
        return [0, 0]

    rx, ry = best_res
    curd = myd[sy][sx]
    best_move = (0, 0); best_mkey = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny): 
            continue
        md = myd[ny][nx]
        if md >= INF: 
            continue
        od = opd[ny][nx]  # not meaningful, but keeps determinism; use opponent distance to target instead below
        # Prefer moves that get closer to target and keep win likelihood (my faster than opponent)
        my_to_t = myd[ny][rx]
        op_to_t = opd[ry][rx]
        if my_to_t >= INF or op_to_t >= INF:
            my_to_t = INF; op_to_t = INF
        k = (-(abs(my_to_t - (curd - 1))), op_to_t - my_to_t, -my_to_t, -(nx + ny), dx, dy)
        if best_mkey is None or k > best_mkey:
            best_mkey = k; best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]