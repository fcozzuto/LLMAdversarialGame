def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = {(p[0], p[1]) for p in obstacles}
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (not inb(x, y)) or ((x, y) in obs)

    if not resources or blocked(sx, sy):
        return [0, 0]

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
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
    opd = bfs((ox, oy)) if not blocked(ox, oy) else None
    if myd is None:
        return [0, 0]
    if opd is None:
        opd = [[INF]*w for _ in range(h)]

    best_rx = None; best_ry = None; best_val = -INF
    for rx, ry in resources:
        d1 = myd[ry][rx]
        if d1 >= INF:
            continue
        d2 = opd[ry][rx]
        # Prefer resources I reach earlier; if tie, closer distance; if opponent can't reach, dominate.
        val = (d2 - d1) * 100 - d1
        if d2 >= INF:  # opponent unreachable
            val += 10**6
        if val > best_val:
            best_val = val; best_rx = rx; best_ry = ry
    if best_rx is None:
        return [0, 0]

    tx, ty = best_rx, best_ry

    # Evaluate candidate moves by how quickly we close on target and whether we avoid letting opponent close.
    def min_opponent_dist_to_target():
        cur = opd[oy][ox]
        best = cur
        for dx, dy in dirs:
            nx, ny = ox + dx, oy + dy
            if not inb(nx, ny) or blocked(nx, ny): 
                continue
            nd = opd[ny][nx]
            if nd < best:
                best = nd
        return best

    opp_best_after = min_opponent_dist_to_target()

    cur_self_to_target = myd[sy][sx]
    best_move = [0, 0]; best_move_score = -INF
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or blocked(nx, ny):
            continue
        d_self_next = myd[ny][nx]
        if d_self_next >= INF:
            continue
        # Opponent advantage penalty estimate: if opponent can improve while we don't, avoid.
        my_progress = cur_self_to_target - d_self_next
        opp_progress = (opd[oy][ox] - opp_best_after) if opd[oy][ox] < INF else 0
        score = my_progress * 10 - d_self_next
        score -= opp_progress * (1.0 if d_self_next > cur_self_to_target else 0.5)
        # Deterministic tie-break: lexicographic preference over moves list order (already deterministic).
        if score > best_move_score:
            best_move_score = score
            best_move = [dx, dy]
    return best_move