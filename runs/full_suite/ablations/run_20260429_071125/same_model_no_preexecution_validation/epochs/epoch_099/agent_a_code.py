def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(start):
        dist = [[INF] * h for _ in range(w)]
        if not valid(start[0], start[1]): return dist
        dist[start[0]][start[1]] = 0
        q = [(start[0], start[1])]
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

    dS = bfs((sx, sy))
    dO = bfs((ox, oy))

    best = None
    best_score = -INF
    for rx, ry in resources:
        ds = dS[rx][ry]
        if ds >= INF: 
            continue
        do = dO[rx][ry]
        if do >= INF:
            do = INF
        # Favor resources we can beat opponent on; otherwise, minimize disadvantage.
        if do == INF:
            score = 100000 - ds
        else:
            score = (do - ds) * 1000 - ds
            # slight preference to closer even if tied
            score -= 2 * ds
        if score > best_score or (score == best_score and (best is None or (rx, ry) < best)):
            best_score = score
            best = (rx, ry)

    if best is None:
        # No reachable resources: move toward a reachable center-ish cell away from opponent.
        targets = [(w // 2, h // 2), (w // 3, h // 3), (2 * w // 3, 2 * h // 3)]
        tx, ty = min(targets, key=lambda t: abs(t[0] - sx) + abs(t[1] - sy))
        best = (tx, ty)

    tx, ty = best
    # Ensure we have a direction that reduces our distance to target; otherwise, pick best neighbor.
    curd = dS[tx][ty]
    cand = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny): 
            continue
        nd = dS[nx][ny]
        cand.append((nd, abs(nx - ox) + abs(ny - oy), dx, dy))
    if not cand:
        return [0, 0]

    # Primary: decrease our distance-to-target (by decreasing distance-from-start to target proxy not available).
    # Use distance-from-start to target via BFS-from-target approximation by greedy on dS to target:
    # pick neighbor that minimizes dist(start_neighbor, target) which equals bfs-target map; we can't compute that.
    # Instead, use heuristic: choose neighbor with smaller |(dx,dy)-direction| and smaller ds_to_target estimate:
    # Since dS is from start, the correct proxy is: prefer smaller dS[nx][ny] if target is closer along shortest paths.
    # Works well with BFS distances' monotonicity for one-step moves.
    bestn = None
    bestd = INF
    for nd, oppd, dx, dy in cand:
        # prefer neighbors that are closer (lower dS to target) approximated by lowering dS[nx][ny] toward any path;
        # if target is same, keep minimal.
        # Also avoid getting too close to opponent if