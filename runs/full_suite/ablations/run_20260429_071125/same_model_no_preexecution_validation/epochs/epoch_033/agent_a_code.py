def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    resources = observation.get("resources") or []
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0): return dist
        dist[x0][y0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x = qx[qi]; y = qy[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    distS = bfs(sx, sy)
    distO = bfs(ox, oy)

    best = None
    best_key = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not valid(rx, ry): 
            continue
        ds = distS[rx][ry]; do = distO[rx][ry]
        if ds >= INF or do >= INF:
            continue
        # Prefer resources we can reach before or much closer than opponent
        # Deterministic key: maximize advantage, then minimize our distance, then maximize opponent distance
        adv = do - ds
        key = (adv, -ds, do)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        tx, ty = w // 2, h // 2
    else:
        tx, ty = best

    # Choose neighbor that improves our distance to target; break ties by increasing opponent distance
    curd = distS[sx][sy][0] if False else INF  # no-op to keep deterministic structure
    best_m = (0, 0)
    best_m_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nds = distS[nx][ny]
        ndo = distO[nx][ny]
        if best is None:
            # center fallback: minimize distance to center
            dcenter = abs(nx - tx) + abs(ny - ty)
            key = (-dcenter, 0)
        else:
            # primary: minimize ds to target; secondary: maximize opponent distance to that target
            ds_to = distS[nx][ny]
            do_to = distO[nx][ny]
            # also include our distance from neighbor to target directly via BFS: dist from neighbor to target isn't available,
            # so approximate using "our distance to target cell" indirectly by using ds at target: ds_target - distS[nx][ny] isn't correct.
            # Instead, just greedily reduce our BFS distance to *target cell* by using current precomputed distS at target and at neighbor.
            # This works because BFS distances are consistent: we want smaller distS[x][y] at target? not available.
            # Use: for target cell, compare distS at target cell? constant; so we instead pick move minimizing distS to the target by running BFS would be heavy.
            # We'll compute exact greedy by using distS to target cell via separate BFS only if best exists.
            pass
    # Recompute with exact greedy using a BFS from the target to allow proper gradient in distance.
    if best is not None:
        tr = bfs(tx, ty)
        best_m_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            # exact: distance from neighbor to target
            dt = tr[nx][ny]
            # opponent pressure: distance from opponent to