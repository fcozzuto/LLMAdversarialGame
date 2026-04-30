def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (not inb(x, y)) or ((x, y) in obs)

    # If somehow trapped, still return valid.
    if blocked(sx, sy):
        return [0, 0]

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def cheb(a, b): return max(abs(a[0]-b[0]), abs(a[1]-b[1]))

    # Pick target resource: prefer ones we can reach sooner (BFS length), else nearest.
    # To keep fast, BFS once from our position to estimate reachability/length; likewise opponent.
    INF = 10**9
    def bfs(start):
        if blocked(start[0], start[1]): return None
        dist = [[INF]*w for _ in range(h)]
        dist[start[1]][start[0]] = 0
        qx = [start[0]]; qy = [start[1]]; qi = 0
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
    opd = bfs((ox, oy)) if resources else None

    if not resources:
        # No resources: move to the "safest" area (maximize distance to opponent).
        best = (0, None)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if blocked(nx, ny): continue
            key = cheb((nx, ny), (ox, oy))
            if key > best[0]:
                best = (key, [dx, dy])
        return best[1] if best[1] is not None else [0, 0]

    best_res = None
    best_score = None
    for r in resources:
        d1 = myd[r[1]][r[0]] if myd is not None else INF
        d2 = opd[r[1]][r[0]] if opd is not None else INF
        if d1 >= INF:
            continue
        # Score: prioritize we arrive earlier; then closer; then farther from opponent to avoid being contested.
        arrive = (0 if d1 < d2 else 1, d1, d2, -cheb((sx, sy), (ox, oy)), r[0], r[1])
        if best_score is None or arrive < best_score:
            best_score = arrive
            best_res = (r[0], r[1])

    if best_res is None:
        return [0, 0]

    tx, ty = best_res

    # Choose step that best advances toward target; if opponent can take it sooner, also try to reduce their distance.
    best_move = [0, 0]
    best_tuple = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny): continue
        mydist = cheb((nx, ny), (tx, ty))
        opdist = cheb((nx, ny), (ox, oy))
        # Secondary: if opponent closer to target than we are, prioritize blocking by reducing their cheb distance to target.
        opp_to_target = cheb((ox, oy), (tx, ty))
        my_to_target = cheb((sx, sy), (tx, ty))
        block_bias = 0
        if opp_to_target < my_to_target:
            block_bias = cheb((nx, ny), (tx, ty)) + 0.5 * cheb((ox, oy), (tx, ty)) - 0.5 * cheb((ox, oy), (tx, ty))  # deterministic no-op shape
        tup = (mydist, -opdist, block_bias, dx, dy)
        if best_tuple is None or tup < best_tuple:
            best_tuple = tup
            best_move = [dx, dy]

    return best_move if best_move is not None else [0, 0]