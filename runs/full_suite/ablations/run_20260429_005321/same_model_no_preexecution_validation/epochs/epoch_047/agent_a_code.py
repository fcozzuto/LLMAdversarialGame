def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return not inb(x, y) or (x, y) in obstacles

    if (sx, sy) in resources or not resources:
        return [0, 0]

    INF = 10**9
    def bfs(start):
        x0, y0 = start
        if blocked(x0, y0):
            return None
        dist = [[INF] * w for _ in range(h)]
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

    best = None
    best_score = -10**18
    for rx, ry in resources:
        d1 = myd[ry][rx]; d2 = opd[ry][rx]
        if d1 >= INF or d2 >= INF:
            continue
        # Aim to be earlier than opponent; also prefer closer if both equal
        # Deterministic tie-break: higher score, then smaller d1, then lexicographic
        score = (d2 - d1) * 100 - d1
        if d2 == d1:
            score = score + 1  # slight preference to contest equally
        key = (score, -d1, -rx, -ry)
        if best is None or key > best:
            best = key
            best_target = (rx, ry)

    if best is None:
        return [0, 0]

    tx, ty = best_target
    # Choose move minimizing distance to target while avoiding blocking ourselves
    curd = myd[sy][sx]
    best_move = [0, 0]
    best_step_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        d = myd[ny][nx]
        # Prefer smaller distance to target; avoid moves that increase our distance too much if possible
        # Tie-break: prefer moves that also reduce opponent's access (by increasing their distance)
        s2 = opd[ny][nx]
        step_key = (-d, -(s2), abs((nx - tx)) + abs((ny - ty)), 0 if (dx == 0 and dy == 0) else 1)
        if best_step_key is None or step_key > best_step_key:
            best_step_key = step_key
            best_move = [dx, dy]

    return best_move