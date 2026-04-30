def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources") or []
    obs = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obs

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

    dS = bfs(sx, sy)
    dO = bfs(ox, oy)

    # Strategy: if we can race a resource (ahead or tied), pick best advantage.
    # Otherwise, pick a resource that minimizes opponent progress while we still move toward it.
    best_res = None
    best_adv = -INF
    best_sum = INF
    for rx, ry in resources:
        ds = dS[rx][ry]
        do = dO[rx][ry]
        if ds >= INF or do >= INF:
            continue
        adv = do - ds  # positive means we are earlier than opponent
        if adv > best_adv or (adv == best_adv and (ds + do) < best_sum):
            best_adv = adv
            best_sum = ds + do
            best_res = (rx, ry)

    def dist_map_to_resources(distmap):
        best = None
        best_score = -INF
        best_tiebreak = INF
        for rx, ry in resources:
            d1 = distmap[rx][ry]
            if d1 >= INF:
                continue
            d2 = dO[rx][ry]
            adv = d2 - d1
            # Prefer resources we can plausibly win; still allow blocking when behind
            score = adv * 10 - d1
            t = d1 + d2
            if score > best_score or (score == best_score and t < best_tiebreak):
                best_score = score
                best_tiebreak = t
                best = (rx, ry)
        return best

    # If no resources are reachable, head to the most central reachable cell.
    if not resources:
        tx, ty = w // 2, h // 2
    else:
        tx, ty = best_res if best_res is not None else dist_map_to_resources(dS) or (w // 2, h // 2)

    # Evaluate immediate move by resulting advantage toward the chosen target (and other nearby resources as tie-break).
    target_d = dS[tx][ty] if inb(tx, ty) else INF
    best_move = (0, 0)
    best_val = -INF

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Compute value without recomputing BFS: use distances from precomputed maps when possible.
        # dS is distance from current; adjust by one step using Chebyshev lower