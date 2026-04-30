def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources") or []
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0): return dist
        dist[x0][y0] = 0
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    dS = bfs(sx, sy)
    dO = bfs(ox, oy)

    valid_moves = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            valid_moves.append((dx, dy, nx, ny))

    if not resources:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        best = (0, 0, -INF)
        for dx, dy, nx, ny in valid_moves:
            score = -(abs(cx - nx) + abs(cy - ny))
            if score > best[2]:
                best = (dx, dy, score)
        return [best[0], best[1]]

    # Choose a target resource we can reach no later than the opponent (prefer clear advantage),
    # otherwise pick the closest "best race" but avoid moving into positions that worsen our race.
    best_r = None
    best_key = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not valid(rx, ry):
            continue
        ds, do = dS[rx][ry], dO[rx][ry]
        if ds >= INF and do >= INF:
            continue
        # Key: maximize (do - ds) and minimize ds; if tied, prefer lower do.
        key = (-(do - ds), ds, do)
        if best_key is None or key < best_key:
            best_key = key
            best_r = (rx, ry, ds, do)

    rx, ry, ds, do = best_r if best_r is not None else (sx, sy, 0, 0)

    # One-step lookahead: score moves by resulting distance to target and to opponent at that target.
    # Also add a small penalty for increasing our distance to the target.
    best_move = (0, 0)
    best_score = -INF
    for dx, dy, nx, ny in valid_moves:
        # Distance estimates from neighbor by BFS tables.
        new_ds = dS[nx][ny]
        to_target = dS[nx][ny]  # not directly; use distance from neighbor to target via reverse BFS not available
        # Use heuristic: Euclidean/Manhattan towards target as tie-breaker (deterministic).
        dist_heur = abs(rx - nx) + abs(ry - ny)
        # Race pressure: smaller ds-to-target is good; approximate with ds_target_delta heuristic from dS already:
        # Compare our current ds to target against opponent race; use dS[target] difference unchanged,
        # so we instead prefer moves that reduce dist_heur; and if already winning, keep tight.
        win_bias = 1 if ds <= do else 0
        score = (100 if win_bias and ds <= do else 0) - dist_heur * (2 if win_bias