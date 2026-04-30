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
        if not valid(x0, y0):
            return dist
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

    if not resources:
        return [0, 0]

    distS = bfs(sx, sy)
    distO = bfs(ox, oy)

    best_r = None
    best_key = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not valid(rx, ry):
            continue
        ds = distS[rx][ry]
        if ds >= INF:
            continue
        do = distO[rx][ry]
        if do >= INF:
            do = INF
        lead = do - ds  # positive means we are closer
        # Deterministic tie-breakers: favor larger lead, then smaller ds, then farther-from-center to reduce symmetry.
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        center_bias = (rx - cx) * (rx - cx) + (ry - cy) * (ry - cy)
        key = (lead, -ds, int(center_bias * 1000), -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    if best_r is None:
        return [0, 0]

    tx, ty = best_r
    ds_t = distS[tx][ty]
    if ds_t >= INF:
        return [0, 0]

    # Choose move that strictly improves distance when possible; otherwise minimize distance and avoid stepping onto opponent path preference.
    best_step = (0, 0)
    best_step_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nds = distS[nx][ny]
        # primary: minimize distance to target; secondary: maximize lead at that step (do - ds)
        ndo = distO[nx][ny]
        lead_here = ndo - nds if (ndo < INF and nds < INF) else -INF
        # last tie-breaker: prefer smaller step toward target deterministically
        step_to = abs(tx - nx) + abs(ty - ny)
        key = (-int(nds), int(lead_here), -step_to, dx, dy)
        if best_step_key is None or key > best_step_key:
            best_step_key = key
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]