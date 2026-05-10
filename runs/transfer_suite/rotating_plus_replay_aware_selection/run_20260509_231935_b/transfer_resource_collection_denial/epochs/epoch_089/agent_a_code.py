def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])

    res_raw = observation.get("resources", []) or []
    obs_raw = observation.get("obstacles", []) or []
    resources = [(p[0], p[1]) for p in res_raw if p and len(p) >= 2]
    obstacles = set((p[0], p[1]) for p in obs_raw if p and len(p) >= 2)

    dirs = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def bfs(start):
        dist = [[10**9] * h for _ in range(w)]
        if not inb(start[0], start[1]) or start in obstacles:
            return dist
        q = [start]
        dist[start[0]][start[1]] = 0
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if not inb(nx, ny) or (nx, ny) in obstacles:
                    continue
                if nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))

    if not resources:
        best = [0, 0]
        bestv = -10**9
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            v = -(abs(nx - ox) if abs(nx - ox) > abs(ny - oy) else abs(ny - oy))
            if v > bestv:
                bestv = v
                best = [dx, dy]
        return best

    best_target = None
    best_val = -10**18
    for rx, ry in resources:
        md = myd[rx][ry]
        od = opd[rx][ry]
        if md >= 10**9:
            continue
        if od >= 10**9:
            val = 10**6 - md
        else:
            val = (od - md) * 1000 - md
        if val > best_val:
            best_val = val
            best_target = (rx, ry)

    if best_target is None:
        return [0, 0]

    tx, ty = best_target
    best_step = [0, 0]
    best_dist = myd[sx][sy]
    # Deterministic first-step selection among shortest paths
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        if myd[nx][ny] < best_dist and myd[nx][ny] <= myd[sx][sy]:
            best_dist = myd[nx][ny]
            best_step = [dx, dy]
    # If somehow no decreasing step, stay
    return best_step