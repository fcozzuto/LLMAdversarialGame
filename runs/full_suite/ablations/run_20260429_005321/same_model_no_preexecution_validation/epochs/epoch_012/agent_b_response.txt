def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h

    INF = 10**9
    def bfs(start):
        x0, y0 = start
        dist = [[INF] * w for _ in range(h)]
        if not inb(x0, y0) or (x0, y0) in obstacles:
            return dist
        dist[y0][x0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x = qx[qi]; y = qy[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    dist_s = bfs((sx, sy))
    dist_o = bfs((ox, oy))

    def valid_moves():
        out = []
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                out.append((dx, dy, nx, ny))
        return out

    moves = valid_moves()
    if not moves:
        return [0, 0]

    if not resources:
        tx, ty = (w - 1) // 2, (h - 1) // 2
        best = None
        for dx, dy, nx, ny in moves:
            val = abs(nx - tx) + abs(ny - ty)
            if best is None or val < best[0]:
                best = (val, dx, dy)
        return [best[1], best[2]]

    my_best = INF
    best_move = (INF, 0, 0)

    for r in resources:
        rx, ry = r
        if (rx, ry) in obstacles:
            continue
        ds = dist_s[ry][rx]
        if ds >= INF:
            continue
        do = dist_o[ry][rx]
        # prefer resources I'm closer to than opponent; still pursue if opponent unreachable
        rel = 0 if do >= INF else do - ds
        # base objective: minimize my distance, maximize advantage
        obj = ds - 0.6 * rel

        # evaluate moves that reduce distance to this resource
        for dx, dy, nx, ny in moves:
            dns = dist_s[ny][nx]
            if dns >= INF:
                continue
            # only consider if this move heads toward (not farther) for stability
            if dns > ds:
                continue
            cand = obj + 0.1 * dns
            if cand < my_best or (cand == my_best and (dx, dy) < (best_move[1], best_move[2])):
                my_best = cand
                best_move = (cand, dx, dy)

    if my_best < INF:
        return [best_move[1], best_move[2]]

    # Fallback: take move minimizing (my distance to closest reachable resource), then tie-break by (dx,dy)
    # Also slight preference to increase distance from opponent to reduce interference.
    closest_res = []
    for r in resources:
        rx, ry = r
        if (rx, ry) in obstacles:
            continue
        ds = dist_s[ry][rx]
        if ds < INF:
            closest_res.append((ds, rx, ry))
    if not closest_res:
        return [0, 0]

    closest_res.sort()
    for dx, dy, nx, ny in moves:
        # compute closest resource distance from this next cell
        nds = INF
        for ds, rx, ry in closest_res:
            v = dist_s[ny][nx]
            # use target-specific ds via manhattan fallback if dist_s unreachable (rare due to ds<INF)
            if v < nds