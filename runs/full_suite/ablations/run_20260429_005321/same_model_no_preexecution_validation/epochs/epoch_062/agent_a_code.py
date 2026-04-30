def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = {(p[0], p[1]) for p in obstacles}
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (not inb(x, y)) or ((x, y) in obs)

    if blocked(sx, sy): return [0, 0]
    if not resources: return [0, 0]

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

    opd = bfs((ox, oy))
    if opd is None: opd = [[INF] * w for _ in range(h)]

    res_sorted = sorted((r[0], r[1]) for r in resources)
    best_move = [0, 0]; best_val = -10**18

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny): continue
        myd = bfs((nx, ny))
        if myd is None: continue

        # Prefer states where we can secure a resource earlier than opponent.
        # Also include a small "safety" term: avoid moving toward opponent when tied.
        val = 0
        tie = 0
        for rx, ry in res_sorted:
            dm = myd[ry][rx]; do = opd[ry][rx]
            if dm >= INF or do >= INF: continue
            gap = do - dm  # positive is good (we are earlier)
            if gap > 0:
                val += 200 + 20 * gap - dm
            elif gap == 0:
                tie += 1
                val += 5 - dm
            else:
                val += gap  # small penalty
        # Opponent proximity penalty (deterministic, lightweight)
        cheb = abs(nx - ox); cheb = cheb if cheb > abs(ny - oy) else abs(ny - oy)
        val -= 2 * (1 if cheb <= 2 else 0)

        # Deterministic tie-breaker: prefer lexicographically smaller moves
        if val > best_val or (val == best_val and (dx, dy) < (best_move[0], best_move[1])):
            best_val = val
            best_move = [dx, dy]

    return best_move