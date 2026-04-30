def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return not inb(x, y) or (x, y) in obstacles
    INF = 10**9

    def bfs(start):
        x0, y0 = start
        if blocked(x0, y0):
            return None
        dist = [[INF]*w for _ in range(h)]
        dist[y0][x0] = 0
        qx = [x0]; qy = [y0]; qi = 0
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
    opd = bfs((ox, oy))
    if myd is None or opd is None:
        return [0, 0]

    # Choose target: prefer resources we can reach not much later than opponent.
    best_rx, best_ry = resources[0]
    best_key = None
    for rx, ry in resources:
        d1 = myd[ry][rx]; d2 = opd[ry][rx]
        if d1 >= INF:
            continue
        # Key: smaller is better. Strongly bias against letting opponent be much earlier.
        key = (d1 - d2, d1, -rx, -ry)
        if best_key is None or key < best_key:
            best_key = key
            best_rx, best_ry = rx, ry

    tx, ty = best_rx, best_ry

    # If opponent is already closer by a margin, try to "herd" toward a different resource.
    # Deterministic alternative target selection.
    dmine = myd[ty][tx]; dop = opd[ty][tx]
    if dop + 2 < dmine and len(resources) > 1:
        alt = None; alt_key = None
        for rx, ry in resources:
            d1 = myd[ry][rx]; d2 = opd[ry][rx]
            if d1 >= INF:
                continue
            key = (d2 - d1, d2, d1, rx, ry)  # prefer where opponent not too early
            if alt_key is None or key < alt_key:
                alt_key = key
                alt = (rx, ry)
        if alt is not None:
            tx, ty = alt

    # Pick move that improves our outcome vs opponent for the chosen target, with tie-breakers.
    best_move = [0, 0]
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        d1n = myd[ny][nx]  # our distance from start to this cell (monotone for BFS)
        dtn = myd[ty][tx]  # constant; keep simple
        my_to_target = myd[ny][tx]  # distance from candidate cell to target
        op_to_target = opd[oy][ox]  # not used directly; keep deterministic
        # Objective: minimize (our distance to target) and maximize slack vs opponent.
        # We estimate opponent's advantage using precomputed distance to target.
        my_to_target = myd[ty][nx] if myd[ty][nx] < INF else INF
        op_to_target = opd[ty][ox] if False else opd[ty][tx]  # opd[ty][tx] already exists, use it
        if op_to_target >= INF or my_to_target >= INF:
            continue
        val = (my_to_target - op_to_target, my_to_target, abs(nx - tx) + abs(ny - ty), dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move