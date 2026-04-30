def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = {(p[0], p[1]) for p in obs_list}
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    INF = 10**9

    def bfs(start):
        x0, y0 = start
        dist = [[INF] * w for _ in range(h)]
        if not inb(x0, y0) or (x0, y0) in obstacles:
            return dist
        dist[y0][x0] = 0
        qx, qy, qi = [x0], [y0], 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))

    best_r = None
    best_sc = -10**18
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        md = myd[ry][rx]
        if md >= INF:
            continue
        od = opd[ry][rx]
        # Prefer resources where we are closer than opponent; still go for them if opponent is far.
        sc = (2000 if od >= INF else 400 * (od - md)) - 3 * md
        if sc > best_sc:
            best_sc = sc
            best_r = (rx, ry)

    # If no reachable resource, drift away from opponent (or stay if blocked).
    if best_r is None:
        tx, ty = sx, sy
        best_move = (0, 0)
        best_key = (-INF, -INF)
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            od_here = (abs(nx - ox) + abs(ny - oy))
            key = (od_here, -(abs(nx - tx) + abs(ny - ty)))
            if key > best_key:
                best_key = key
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    rx, ry = best_r
    cur_md = myd[sy][sx]
    chosen = (0, 0)
    chosen_key = (-10**18, -10**18, -10**18)

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nmd = myd[ny][nx]
        nod = opd[ny][nx] if inb(nx, ny) else INF  # distance from opponent to that cell (for tie-break)
        # Key: primarily minimize distance to target, secondarily keep away from opponent if tied.
        # Deterministic tie-break order by move vector embedded via tuple ordering.
        step_gain = (cur_md - nmd)
        key = (step_gain, -(abs(nx - ox) + abs(ny - oy)), -nmd)
        if key > chosen_key:
            chosen_key = key
            chosen = (dx, dy)

    return [chosen[0], chosen[1]]