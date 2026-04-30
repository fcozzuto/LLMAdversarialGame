def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}

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
            x, y = qx[qi], qy[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))

    if not resources:
        return [0, 0]

    # Choose target deterministically: prefer resources we can reach earlier; otherwise nearest we can reach.
    best = None
    for rx, ry in resources:
        md = myd[ry][rx]
        if md >= INF: 
            continue
        od = opd[ry][rx]
        if od >= INF:
            od = INF
        # Primary: earlier arrival (strict), Secondary: larger advantage, Tertiary: shorter time, Quaternary: lexicographic
        strict = 1 if md < od else 0
        key = (strict, od - md, -md, rx, ry)
        if best is None or key > best[0]:
            best = (key, (rx, ry), md, od)

    if best is None:
        return [0, 0]
    (_, (tx, ty), _, _) = best

    # Pick move by local evaluation toward target; avoid stepping into obstacles/out-of-bounds.
    best_move = [0, 0]
    best_val = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d_to = myd[ny][nx] if myd[ny][nx] < INF else (max(abs(tx - nx), abs(ty - ny)))
        # Prefer reducing distance to target; penalize moves that give opponent a big advantage to same target
        od_here = opd[ty][tx]  # constant for target; keep deterministic
        # Use opponent distance from their next step to break ties subtly
        opp_best = INF
        for pdx, pdy in dirs:
            qx, qy = ox + pdx, oy + pdy
            if inb(qx, qy) and (qx, qy) not in obstacles:
                opp_best = min(opp_best, opd[qy][qx] + 1)
        val = (d_to, abs(nx - tx) + abs(ny - ty), od_here, opp_best, dx, dy)
        if best_val is None or val < best_val:
            best_val = val
            best_move = [dx, dy]

    return best_move