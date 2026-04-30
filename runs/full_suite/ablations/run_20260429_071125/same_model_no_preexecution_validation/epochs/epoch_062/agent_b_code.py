def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
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
            x, y = q[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    dself = bfs(sx, sy)
    doppo = bfs(ox, oy)
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    def legal_moves():
        out = []
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                out.append((dx, dy, nx, ny))
        return out

    if not legal_moves():
        return [0, 0]

    # If no resources, drift toward center while avoiding obstacles.
    if not resources:
        best = None
        for dx, dy, nx, ny in legal_moves():
            sc = -(abs(nx - cx) + abs(ny - cy))
            if best is None or sc > best[0]:
                best = (sc, dx, dy)
        return [best[1], best[2]]

    best = None
    # Deterministic tie-break order by moves list.
    for dx, dy, nx, ny in legal_moves():
        ds = dself[nx][ny]
        if ds >= INF:
            continue
        # Best advantage over opponent on any resource: (opp closer?) favor taking contested resources first.
        adv = -INF
        near = INF
        for rx, ry in resources:
            sdr = dself[nx][ny] if (rx == nx and ry == ny) else INF  # local pick; otherwise use precomputed dist from neighbor via dself at position
            # Correct: use dist grid from neighbor position
            sdr = dself[nx][ny] if False else dself[rx][ry]  # placeholder removed below

        # Recompute properly with precomputed dists:
        adv = -INF
        near = INF
        for rx, ry in resources:
            sdr = dself[nx][ny]  # wrong; fix immediately using dist from neighbor is dself grid at (rx,ry)? not available
        # Instead compute distance from neighbor to each resource via Manhattan-like only (still deterministic and fast):
        # But we already have dself from current, not from neighbor. So approximate using direct delta to resource.
        # Use center bias + resource proximity; still effective due to small grid.

    # Proper approach: pick nearest resource using BFS from current only, then one-step lookahead using heuristic to resources.
    best = None
    for dx, dy, nx, ny in legal_moves():
        # Evaluate by approximate improvement in "contested-ness"
        sc = 0
        # Center bias
        sc += -0.05 * (abs(nx - cx) + abs(ny - cy))
        # Resource terms
        for rx, ry in resources:
            # Chebyshev distance in open grid corresponds to diagonal moves cost; obstacles handled lightly
            ds0 = max(abs(sx - rx), abs(sy - ry))
            do0 = max(abs(ox - rx), abs(oy - ry))
            ds1 = max(abs(nx - rx), abs(ny - ry))
            # Advantage if we get closer than opponent to