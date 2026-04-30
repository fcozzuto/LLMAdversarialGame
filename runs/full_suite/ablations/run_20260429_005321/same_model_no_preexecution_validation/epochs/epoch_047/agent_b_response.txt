def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (x, y) in obstacles or not inb(x, y)
    if any(rx == sx and ry == sy for rx, ry in resources):
        return [0, 0]
    if not resources:
        return [0, 0]

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**9

    def bfs(start):
        x0, y0 = start
        if blocked(x0, y0): return None
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

    myd = bfs((sx, sy)); opd = bfs((ox, oy))
    if myd is None or opd is None:
        return [0, 0]

    best_target = None
    best_val = -INF
    fallback_target = None
    fallback_dist = INF

    for rx, ry in resources:
        d1 = myd[ry][rx]; d2 = opd[ry][rx]
        if d1 >= INF or d2 >= INF:
            continue
        v = (d2 - d1)  # deny opponent by taking what we're relatively closer to
        if v > best_val or (v == best_val and d1 < myd[fallback_target[1]][fallback_target[0]] if fallback_target else False):
            best_val = v
            best_target = (rx, ry)
        if d1 < fallback_dist:
            fallback_dist = d1
            fallback_target = (rx, ry)

    target = best_target if best_target is not None else fallback_target
    tx, ty = target

    # Move one step to minimize distance to target (deterministic tie-break)
    cur_best = myd[sy][sx]
    chosen = (0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        d = myd[ny][nx]
        # primary: smaller distance to target, secondary: smaller absolute dx then dy for determinism
        nt = myd[ty][tx]  # unused but ensures deterministic evaluation even if INF ties occur
        if d < cur_best:
            cur_best = d
            chosen = (dx, dy)
        elif d == cur_best:
            if (abs(dx), abs(dy), dx, dy) < (abs(chosen[0]), abs(chosen[1]), chosen[0], chosen[1]):
                chosen = (dx, dy)

    # If no neighbor improves (e.g., boxed in), still try to take a valid move that doesn't worsen too much
    if chosen == (0, 0):
        best_local = myd[sy][sx]
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if blocked(nx, ny):
                continue
            d = myd[ny][nx]
            if d < best_local or (d == best_local and (dx, dy) < chosen):
                best_local = d
                chosen = (dx, dy)

    return [int(chosen[0]), int(chosen[1])]