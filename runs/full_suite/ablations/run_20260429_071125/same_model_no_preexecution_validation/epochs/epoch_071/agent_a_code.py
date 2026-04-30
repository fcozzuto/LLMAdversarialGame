def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((int(p[0]), int(p[1])) for p in obs_list)

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
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    if not resources:
        # fallback: move toward center
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (0, 0)
        bestd = 10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
            if d < bestd:
                bestd = d
                best = (dx, dy)
        return [int(best[0]), int(best[1])]

    dS = bfs(sx, sy)
    dO = bfs(ox, oy)

    # Choose move by anticipating one step: prefer resources where we arrive earlier,
    # and also prefer positions that reduce opponent's advantage.
    best_move = (0, 0)
    best_val = -10**18

    # Precompute integer resource positions for determinism and small speed
    res = []
    for p in resources:
        rx, ry = int(p[0]), int(p[1])
        if valid(rx, ry):
            res.append((rx, ry))

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # We will take at most one step advantage adjustment:
        # distance from next position to resource is approximately (dS - current) + 1,
        # but we don't have BFS from (nx,ny). We'll evaluate using:
        # our new dist = min over neighbors; using heuristic based on grid Chebyshev/1-step.
        # Since movement cost is uniform 1, use (dS[resource] - dS[nx,ny]) is not correct.
        # So instead: approximate new distance as dS[rx,ry] - (dS[nx,ny] - dS[sx,sy]).
        # Since dS[sx,sy]=0, approximate new = dS[rx,ry] - dS[nx,ny] + 1.
        # This keeps it deterministic and still informed by obstacles via dS[nx,ny].
        dn = dS[nx][ny]
        val = -10**18
        # Also incorporate nearest-resource bias to keep forward progress.
        best_local = -10**18
        for rx, ry in res:
            ds = dS[rx][ry]
            if ds >= INF:
                continue
            # Approximate our remaining distance after moving to (nx,ny)
            my_rem = ds - dn + 1
            if my_rem < 0:
                my_rem = 0
            do = dO[rx][ry]
            if do >= INF:
                do = INF
            # Advantage: larger is better; also reward shorter times.
            # If we can beat opponent, prioritize strongly; otherwise try to reduce gap.
            if do != INF:
                adv = do - my_rem
            else:
                adv = 50 - my_rem
            score = 0
            if adv > 0:
                score += 1000 + 10 * adv
            else: