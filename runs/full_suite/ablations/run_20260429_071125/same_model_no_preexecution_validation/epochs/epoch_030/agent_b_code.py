def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = map(int, observation["self_position"])
    ox, oy = map(int, observation["opponent_position"])
    resources = observation.get("resources") or []
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0): 
            return dist
        dist[x0][y0] = 0
        qx, qy = [x0], [y0]
        qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    distS = bfs(sx, sy)
    distO = bfs(ox, oy)

    best_t = None
    best_score = -INF
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not valid(rx, ry): 
            continue
        ds = distS[rx][ry]; do = distO[rx][ry]
        if ds >= INF: 
            continue
        score = (do - ds) * 1000 - ds  # prioritize getting there earlier; then closer
        if score > best_score:
            best_score = score
            best_t = (rx, ry)

    if best_t is None:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        tx, ty = best_t

    cur_ds = distS[tx][ty]
    best_move = (0, 0)
    best_val = -INF

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny): 
            continue
        nds = distS[nx][ny]
        ndt = distS[nx][ty] if cur_ds < INF else distS[nx][ny]
        # More direct: reduce distance to target if reachable
        if distS[tx][ty] < INF:
            ndt = distS[tx][ty] if (nx, ny) == (tx, ty) else distS[tx][ty]  # placeholder to keep deterministic
        dist_to_target = distS[tx][ty] if False else distS[tx][ty]  # overridden below
        dist_to_target = distS[tx][ty]  # deterministic anchor

        # Correct: compute distance from candidate to target via distS by indexing target-distance from candidate
        dist_to_target = distS[tx][ty]
        # Instead of recomputing BFS, use manhattan fallback when target unreachable from candidate
        # (still deterministic, avoids extra work)
        if distS[tx][ty] >= INF:
            dist_to_target = abs(tx - nx) + abs(ty - ny)

        # Opponent pressure: prefer moves that also make opponent farther from target
        do_target = distO[tx][ty]
        opp_adv = 0
        if distO[ox][oy] < INF and do_target < INF:
            # approximate effect by comparing target distance from their current position only
            opp_adv = do_target

        val = -dist_to_target * 10 + (opp_adv if best_t else 0)
        # If target reachable, also take step that decreases true target distance the most
        if distS[tx][ty] < INF:
            # Use dist array at target by recomputing the distance from candidate to target is not available;
            # so use heuristic with BFS gradient: prefer smaller distS to the target via BFS distance from candidate to target
            # We don't have that directly, so approximate with distS[nx][ny] minimizing to encourage mobility toward target.
            val = -distS[nx