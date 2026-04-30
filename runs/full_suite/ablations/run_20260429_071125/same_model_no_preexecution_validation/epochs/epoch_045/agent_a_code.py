def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    if not resources:
        return [0, 0]

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

    distS = bfs(sx, sy)
    distO = bfs(ox, oy)

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    target_score = []
    for rx, ry in resources:
        dS = distS[rx][ry]
        dO = distO[rx][ry]
        if dS >= INF and dO >= INF:
            continue
        if dS >= INF:
            pri = (-10**6, 10**6, (rx - cx) ** 2 + (ry - cy) ** 2)
        elif dO >= INF:
            pri = (10**6, dS, (rx - cx) ** 2 + (ry - cy) ** 2)
        else:
            pri = (dO - dS, dS, (rx - cx) ** 2 + (ry - cy) ** 2)
        target_score.append((pri, (rx, ry)))
    if not target_score:
        return [0, 0]
    target_score.sort(reverse=True)
    tgt = target_score[0][1]

    best = None
    best_val = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Evaluate by how much this move improves our lead to the best available resource,
        # with a small center preference and a slight "chase" to opponent for contests.
        local_best = (-10**9, 10**9, 10**18)
        for rx, ry in resources:
            dSn = distS[nx][ny]  # approximation: dist from nx,ny to target not computed
            # Instead use precomputed distS at target: prefer moving toward tgt direction quickly.
            # Compute exact step-to-tgt metric only for speed.
            d1 = abs(nx - rx) + abs(ny - ry)
            d2 = abs(ox - rx) + abs(oy - ry)
            # Use manhattan-to-resource as proxy for ordering; scaled to emphasize lead.
            lead = (d2 - d1)
            center = (nx - cx) ** 2 + (ny - cy) ** 2
            cand = (lead, d1, center)
            if cand > local_best:
                local_best = cand
        # Deterministic tie-break: prefer smaller distance to main target and then lexicographic move.
        dist_to_tgt = abs(nx - tgt[0]) + abs(ny - tgt[1])
        val = (local_best[0], -dist_to_tgt, -local_best[1], -(local_best[2]))
        if best is None or val > best_val:
            best = (dx, dy)
            best_val = val

    return [int(best[0]), int(best[1])] if best is not None else [0, 0]