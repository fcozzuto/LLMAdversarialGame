def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)
    dirs8 = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x,y): return 0 <= x < w and 0 <= y < h
    def blocked(x,y): return (not inb(x,y)) or ((x,y) in obs)

    if not resources or blocked(sx, sy) or blocked(ox, oy):
        return [0, 0]

    mypos = (sx, sy); opp = (ox, oy)

    INF = 10**9
    def bfs_from(start):
        if blocked(start[0], start[1]): return None
        dist = [[INF]*w for _ in range(h)]
        x0, y0 = start
        dist[y0][x0] = 0
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs8:
                nx, ny = x + dx, y + dy
                if not blocked(nx, ny) and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    q.append((nx, ny))
        return dist

    myd = bfs_from(mypos)
    opd = bfs_from(opp)
    if myd is None or opd is None:
        return [0, 0]

    # Pick a resource that I can reach and that I can beat the opponent to (myd smaller than opd).
    best_r = None
    best_score = -10**18
    for rx, ry in resources:
        d1 = myd[ry][rx]; d2 = opd[ry][rx]
        if d1 >= INF or d2 >= INF:
            continue
        score = (d2 - d1) * 10 - d1
        if score > best_score:
            best_score = score
            best_r = (rx, ry)

    if best_r is None:
        return [0, 0]
    tx, ty = best_r

    # Precompute opponent nearest resource distance for tie-breaking.
    opp_best = INF
    for rx, ry in resources:
        d2 = opd[ry][rx]
        if d2 < opp_best:
            opp_best = d2

    best_move = (0, 0)
    best_mkey = None
    for dx, dy in dirs8:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        # Prefer moves that reduce distance to target; then increase opponent's advantage.
        my_to_t = myd[ny][nx]  # distance from current to next? (approx): better use from next to target via BFS to target
        # Approximate next->target using current BFS by symmetry is not exact; recompute only target distances with BFS from next if needed.
        # Since grid is tiny, do exact check by local BFS from (nx,ny) to target only (use full BFS for simplicity).
        md_next = bfs_from((nx, ny))
        if md_next is None:
            continue
        d_next = md_next[ty][tx]
        if d_next >= INF:
            continue
        # Opponent "pressure" proxy: target distance from opponent
        opp_press = opd[ty][tx]
        mkey = (d_next, -opp_press, 0)
        if best_mkey is None or mkey < best_mkey:
            best_mkey = mkey
            best_move = (dx, dy)

    # If stuck by obstacles (shouldn't), stay.
    if blocked(sx + best_move[0], sy + best_move[1