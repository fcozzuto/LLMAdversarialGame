def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    obs_list = observation.get("obstacles") or []
    obstacles = set((int(p[0]), int(p[1])) for p in obs_list)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
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
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    if not resources:
        return [0, 0]

    distS = bfs(sx, sy)
    distO = bfs(ox, oy)

    best = None
    best_score = -INF
    for tx, ty in resources:
        ds, do = distS[tx][ty], distO[tx][ty]
        if ds >= INF and do >= INF:
            continue
        if ds < INF and do >= INF:
            adv = 10**6
        else:
            adv = do - ds  # positive => we are closer
        # prefer winning races; then shorter ours
        s = adv * 1000 - ds
        if best is None or s > best_score:
            best_score = s
            best = (tx, ty, ds, do)
    if best is None:
        return [0, 0]
    tx, ty, _, _ = best

    # Choose move that most reduces our distance to target, but also avoids giving opponent an immediate capture.
    cur_d = distS[tx][ty]
    cand = (0, 0)
    best_v = -INF
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ndS = distS[tx][ty] if cur_d >= INF else bfs(nx, ny)[tx][ty]
        # local opponent pressure: penalize if we move toward opponent and they are closer to the same target
        do_t = distO[tx][ty]
        opp_close = 0
        if do_t < INF and do_t <= 2:
            # estimate opponent distance after their likely move: use current distS to their position as proxy
            # deterministic proxy: penalize moving closer to opponent
            opp_close = -1
        # Use our current distance field by re-running small BFS only when needed is too costly; so derive from current distS:
        # Prefer decreasing distS to target: exact with BFS from candidate; keep it deterministic.
        # Add slight tie-break toward board center.
        cx, cy = (w - 1) // 2, (h - 1) // 2
        center = - (abs(nx - cx) + abs(ny - cy))
        v = (-(ndS) if ndS < INF else -10**6) * 10 + center + opp_close
        if v > best_v:
            best_v = v
            cand = (dx, dy)

    dx, dy