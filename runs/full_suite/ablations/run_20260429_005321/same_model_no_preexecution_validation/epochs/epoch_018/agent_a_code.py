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
        qx, qy = [x0], [y0]
        qi = 0
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

    best = None
    best_key = (-INF, -INF, INF)
    for rx, ry in resources:
        if (rx, ry) in obstacles:
            continue
        md = myd[ry][rx]
        if md >= INF:
            continue
        od = opd[ry][rx]
        if od >= INF:
            od = INF
        diff = od - md
        tie_my = -md
        # Maximize diff; then prefer smaller my distance; then prefer larger opponent distance.
        key = (diff, tie_my, od)
        if key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best if best is not None else (w // 2, h // 2)

    # Move that minimizes distance to target (my BFS distance); deterministic tie-breaking by dirs order.
    cur = myd[sy][sx]
    chosen = (0, 0)
    chosen_d = myd[sy][sx]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = myd[ny][nx]
        # Prefer reaching target region; don't get worse if already at same best.
        if d < chosen_d or (d == chosen_d and (dx, dy) < chosen):
            chosen_d = d
            chosen = (dx, dy)

    return [int(chosen[0]), int(chosen[1])]