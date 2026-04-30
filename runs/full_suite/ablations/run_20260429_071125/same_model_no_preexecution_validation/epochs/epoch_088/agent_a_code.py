def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources") or []
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0):
            return dist
        dist[x0][y0] = 0
        qx, qy = [x0], [y0]
        qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx)
                    qy.append(ny)
        return dist

    dS = bfs(sx, sy)
    dO = bfs(ox, oy)

    # Choose a target that we can reach sooner than opponent (maximize do-ds),
    # while preferring closer targets if advantage is similar.
    best = None
    best_adv = -INF
    best_ds = INF
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not valid(rx, ry):
            continue
        ds = dS[rx][ry]
        if ds >= INF:
            continue
        do = dO[rx][ry] if valid(ox, oy) else INF
        if do >= INF:
            adv = ds  # if opponent can't reach, prioritize still being feasible (lower ds better)
        else:
            adv = do - ds
        if do >= INF:
            score_adv = INF - ds  # higher when ds is smaller
        else:
            score_adv = adv
        if score_adv > best_adv or (score_adv == best_adv and ds < best_ds):
            best_adv = score_adv
            best_ds = ds
            best = (rx, ry)

    if best is None:
        # Fallback: move to any valid neighboring cell that increases distance from opponent if possible
        candidates = []
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                dist_opp = abs(nx - ox) + abs(ny - oy)
                candidates.append((dist_opp, nx, ny, dx, dy))
        if not candidates:
            return [0, 0]
        candidates.sort(reverse=True)
        return [candidates[0][3], candidates[0][4]]

    tx, ty = best

    # Pick next step that keeps us moving toward target with minimal self distance;
    # break ties by maximizing opponent distance advantage after the move.
    best_move = (0, 0)
    best_rank = (-INF, INF, INF)  # (opp_d, ds_next, lex)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds_next = dS[nx][ny] if valid(nx, ny) else INF
        # Reuse precomputed distances to target: prefer smaller dS[target] among reachable neighbors.
        # Since we don't have dS for (nx->target) directly, approximate by dS[nx][tx,ty] isn't available;
        # instead use Manhattan tie-break toward target and dist-to-target in BFS grid via precomputed dS.
        # We can get dist from neighbor to target by running BFS from neighbor, but too costly; use heuristic:
        man_to_target = abs(nx - tx) + abs(ny - ty)
        opp_dist = abs(nx - ox) + abs(ny - oy)
        rank = (opp_dist, man_to_target, ds_next)
        if rank[0] > best_rank[0] or (rank[0] == best_rank[0] and (rank[1], rank[2]) < (best_rank[1