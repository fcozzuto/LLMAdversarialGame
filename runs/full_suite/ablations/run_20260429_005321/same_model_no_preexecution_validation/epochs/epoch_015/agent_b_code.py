def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h

    INF = 10**9
    def bfs(start):
        x0, y0 = start
        dist = [[INF]*w for _ in range(h)]
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

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))

    # Pick a target resource: prefer (opd - myd) advantage; otherwise closest to us.
    best_r = None
    best_sc = -10**18
    for rx, ry in resources:
        md = myd[ry][rx]
        if md >= INF: 
            continue
        od = opd[ry][rx]
        if od >= INF:
            sc = 10**6 - md  # we can reach, opponent can't
        else:
            adv = od - md
            sc = adv*1000 - md*5 - od*2  # strong pull to win races, slight preference for quick capture
        if sc > best_sc:
            best_sc = sc
            best_r = (rx, ry)

    # If no reachable resource, just head to the closest non-obstacle cell to opponent to contest.
    if best_r is None:
        tx, ty = ox, oy
    else:
        tx, ty = best_r

    # Choose move that improves our distance to target; ties prefer moving away from opponent.
    curd = myd[ty][tx]
    best_move = (0, 0)
    best1 = 10**18
    best2 = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_to = myd[ny][nx]
        # d_to computed for target won't be right; use dist from candidate to target via myd[target] is reverse BFS not available.
        # Instead, approximate by stepping closer based on BFS gradient from candidate using myd to target? Not stored.
        # Use immediate greedy metric: Chebyshev distance to target.
        mdist = max(abs(tx - nx), abs(ty - ny))
        oppdist = max(abs(ox - nx), abs(oy - ny))
        if mdist < best1 or (mdist == best1 and oppdist > best2):
            best1 = mdist
            best2 = oppdist
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]