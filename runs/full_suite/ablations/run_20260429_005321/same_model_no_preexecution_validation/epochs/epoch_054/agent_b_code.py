def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    if (sx, sy) in obs or (ox, oy) in obs:
        return [0, 0]
    if not resources:
        return [0, 0]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (not inb(x, y)) or ((x, y) in obs)

    INF = 10**9

    def bfs(start):
        x0, y0 = start
        if blocked(x0, y0):
            return None
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

    # deterministic preference: if opponent can't reach, prioritize that; else prioritize where we beat them.
    best = None
    for rx, ry in resources:
        if blocked(rx, ry):
            continue
        d1 = myd[ry][rx]
        d2 = opd[ry][rx]
        if d1 >= INF:
            continue
        # scoring: prefer being closer, and strongly prefer resources opponent can't reach.
        if d2 >= INF:
            score = 10**7 - d1
        else:
            score = (d2 - d1) * 1000 - d1
        # tie-break deterministically
        key = (score, -abs(rx - ox) - abs(ry - oy), -rx, -ry)
        if best is None or key > best[0]:
            best = (key, rx, ry)

    if best is None:
        return [0, 0]
    _, tx, ty = best

    # If already on target, move to reduce distance to next best reachable resource deterministically.
    if (sx, sy) == (tx, ty):
        # choose a deterministic "circling" step: reduce distance to target is zero; pick lexicographically smallest move that is valid.
        best_step = (0, 0)
        bestd = myd[sy][sx]
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if blocked(nx, ny):
                continue
            if myd[ny][nx] < bestd:
                bestd = myd[ny][nx]; best_step = (dx, dy)
            elif myd[ny][nx] == bestd and (dx, dy) < best_step:
                best_step = (dx, dy)
        return [best_step[0], best_step[1]]

    curd = myd[sy][sx]
    best_step = (0, 0)
    best_val = (INF, 0, 0)  # (dist_to_target, lex_x, lex_y)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        # We don't have per-target dist; use myd to target by comparing dist-to-start,
        # but for a greedy step we can just move to a cell that has smaller distance to that target
        # in reverse BFS sense: approximate via euclidean/cheb to target deterministically using only geometry.
        # Since dirs and obstacles matter, also avoid increasing myd distance to reduce getting stuck.
        if myd[ny][nx] > curd:
            continue
        dist_cheb = max(abs(nx - tx), abs(ny - ty))
        val = (dist_cheb, nx, ny)
        if val < best_val:
            best_val = val; best_step = (dx, dy)

    # Fallback if all moves rejected due to myd constraint
    if best_step == (0, 0):
        for dx, dy in dirs:
            nx, ny