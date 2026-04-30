def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
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

    distS = bfs(sx, sy)
    distO = bfs(ox, oy)

    # Choose a target that we can reach first, but prefer locations that are hard for opponent.
    best = None
    best_val = -INF
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not valid(rx, ry): 
            continue
        ds = distS[rx][ry]; do = distO[rx][ry]
        if ds >= INF: 
            continue
        if do >= INF: do = 999999
        # Higher is better: prioritize smaller ds, and larger (do-ds)
        val = (do - ds) * 2 - ds + (abs(rx - sx) + abs(ry - sy)) * 0.01
        if val > best_val:
            best_val = val
            best = (rx, ry, ds, do)

    # If no reachable target, move to maximize distance from opponent while staying valid.
    if best is None:
        best_move = [0, 0]
        best_sc = -INF
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            d_op = abs(nx - ox) + abs(ny - oy)
            sc = d_op - (dx != 0 or dy != 0) * 0.001
            if sc > best_sc:
                best_sc = sc
                best_move = [dx, dy]
        return best_move

    rx, ry, ds, do = best

    # Take a deterministic step that reduces our distance to target; break ties by increasing distance from opponent.
    cur_d = distS[sx][sy]
    best_move = [0, 0]
    best_sc = -INF
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = distS[nx][ny]
        if nd >= INF:
            continue
        step_towards = cur_d - nd  # positive if closer in graph steps
        if step_towards < 0:
            continue
        d_op = abs(nx - ox) + abs(ny - oy)
        # Also discourage stepping into squares where opponent is much closer to the same target.
        opp_nd = distO[nx][ny]
        # If opponent can reach target much sooner, still allow only progress steps.
        sc = step_towards * 100 + d_op * 1.5 - (opp_nd if opp_nd < INF else 1000) * 0.01 + (nx * 0.001 + ny * 0.0001)
        if sc > best_sc:
            best_sc = sc
            best_move = [dx, dy]
    return best_move