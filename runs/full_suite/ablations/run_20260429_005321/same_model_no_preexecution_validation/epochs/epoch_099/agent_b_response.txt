def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])

    obstacles = {(int(p[0]), int(p[1])) for p in (observation.get("obstacles") or [])}
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    dirs8 = [(-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not free(x0, y0):
            return dist
        dist[x0][y0] = 0
        qx, qy, qi = [x0], [y0], 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in dirs8:
                nx, ny = x + dx, y + dy
                if free(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    myd = bfs(sx, sy)
    opd = bfs(ox, oy)

    best = None
    best_val = -10**18
    # Deterministic tie-break using (myd, opd, rx, ry) lexicographic
    for rx, ry in resources:
        dm = myd[rx][ry]
        do = opd[rx][ry]
        if dm >= INF and do >= INF:
            continue
        # Race score: prefer where we beat opponent, and prefer closer pickups
        if dm < do:
            win_margin = (do - dm)
            val = 1e6 * win_margin - dm
        else:
            val = -10**6 * (dm - do) - dm  # discourage losing races
        key = (val, -(do - dm if do < INF and dm < INF else 0), -dm, rx, ry)
        if key > (best_val, 0, 0, -1, -1):
            best_val = key[0]
            best = (rx, ry)

    if best is None:
        # No reachable resource: go toward center deterministically
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        tx, ty = best

    if (sx, sy) == (tx, ty):
        return [0, 0]

    # Choose move that minimizes our distance to target; if tie, maximizes our advantage vs opponent
    best_move = (0, 0)
    cur_dm = myd[sx][sy]
    cur_do = opd[sx][sy]
    chosen = False
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            nx, ny = sx + dx, sy + dy
            if not free(nx, ny):
                continue
            ndm = myd[nx][ny]
            if ndm >= INF:
                continue
            # Advantage after move for target: compare target race distances
            my_to = myd[tx][ty]  # constant
            opp_to = opd[tx][ty]  # constant
            # Use heuristic: prefer reducing our distance to target (ndm + remaining), approximate by ndm
            rem = ndm
            # Additionally, prefer moves that decrease opponent distance to our current position less (stay compact)
            # tie-break uses deterministic order of (ndm, -opd[nx][ny], dx, dy)
            cand = (rem, -opd[nx