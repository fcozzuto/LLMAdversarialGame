def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (not inb(x, y)) or ((x, y) in obs)

    if blocked(sx, sy):
        return [0, 0]

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**9

    def bfs(start):
        if blocked(start[0], start[1]):
            return None
        dist = [[INF] * w for _ in range(h)]
        dist[start[1]][start[0]] = 0
        qx = [start[0]]; qy = [start[1]]; qi = 0
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
    if myd is None:
        return [0, 0]
    opd = bfs((ox, oy)) if not blocked(ox, oy) else None
    if opd is None:
        opd = [[INF] * w for _ in range(h)]

    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in resources:
        d1 = myd[ry][rx]
        d2 = opd[ry][rx]
        if d1 >= INF:
            continue
        contest = 1 if d1 < d2 else 0
        # Prefer contestable + closer; then prefer bigger lead, then prefer higher opponent cost.
        key = (contest, -d1, d2 - d1, d2)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        # No reachable resource: move to minimize distance to opponent or to open space
        tx, ty = ox, oy
    else:
        tx, ty = best

    target_dist = myd[ty][tx] if best is not None else INF

    # Choose a deterministic step that reduces distance to the chosen target if possible.
    candidates = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        if best is not None and myd[ny][nx] < target_dist:
            candidates.append((myd[ny][nx], dx, dy))
        elif best is None:
            candidates.append((abs(nx - ox) + abs(ny - oy), dx, dy))

    if candidates:
        candidates.sort(key=lambda t: (t[0], t[1], t[2]))
        return [candidates[0][1], candidates[0][2]]

    # Otherwise, try any move that minimizes own distance to the target (or stays safe).
    fallback = []
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        fallback.append((myd[ny][nx], dx, dy))
    if not fallback:
        return [0, 0]
    fallback.sort(key=lambda t: (t[0], t[1], t[2]))
    return [fallback[0][1],