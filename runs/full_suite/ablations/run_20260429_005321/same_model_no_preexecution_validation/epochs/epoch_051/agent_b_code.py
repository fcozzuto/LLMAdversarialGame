def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs = set(tuple(p) for p in (observation.get("obstacles") or []))

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (not inb(x, y)) or ((x, y) in obs)

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

    if not resources:
        return [0, 0]

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))
    if myd is None:
        return [0, 0]

    res_set = set(tuple(r) for r in resources)
    if (sx, sy) in res_set:
        return [0, 0]

    best_r = None
    best_key = None
    for rx, ry in resources:
        md = myd[ry][rx]
        if md >= INF: 
            continue
        od = opd[ry][rx] if opd is not None else INF
        # Prefer resources we can beat (smaller opponent time), otherwise deny close ones.
        margin = od - md
        key = (margin, -md, -abs(rx - ox) - abs(ry - oy))
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    tx, ty = best_r if best_r is not None else resources[0]
    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        # Score: improve toward target, but avoid moving into positions opponent can contest sooner.
        my_to_t = myd[ny][nx]  # 0 at current; approximate by dist from current to target via BFS not stored
        # Use precomputed distances to target instead:
        cur_to_t = myd[ty][tx] if (0 <= ty < h and 0 <= tx < w) else INF
        n_to_t = myd[ny][nx]  # not helpful; instead compute n_to_target via BFS dist from nx,ny is unavailable
        # So use Manhattan as tie-breaker; BFS used only for target selection.
        man_t = abs(nx - tx) + abs(ny - ty)
        od_n = opd[ny][nx] if opd is not None else INF
        score = (-man_t, (od_n - md if 'md' in locals() else 0), -abs(nx - ox) - abs(ny - oy))
        if score > best_score:
            best_score = score
            best_move = [dx, dy]

    return best_move