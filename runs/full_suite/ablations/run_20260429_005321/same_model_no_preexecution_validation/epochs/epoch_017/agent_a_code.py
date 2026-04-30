def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obstacles_list)

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    INF = 10**9

    def bfs(start):
        x0, y0 = start
        dist = [[INF] * w for _ in range(h)]
        if not inb(x0, y0) or (x0, y0) in obstacles:
            return dist
        dist[y0][x0] = 0
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    q.append((nx, ny))
        return dist

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))

    # If no resources, just head toward opponent "pressure" point: move toward their nearest reachable resource if any
    if not resources:
        best = None; best_d = INF
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles and myd[ny][nx] < best_d:
                best_d = myd[ny][nx]; best = (nx, ny)
        if best is None: return [0, 0]
        return [best[0] - sx, best[1] - sy]

    best_target = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles: 
            continue
        md = myd[ry][rx]
        if md >= INF: 
            continue
        od = opd[ry][rx]
        # Prefer resources we can reach earlier; strongly deny opponent; then close distance
        if od >= INF:
            key = (3, -md, rx, ry)
        else:
            delta = od - md  # positive means we arrive earlier
            key = (2 if delta >= 0 else 1, delta, -md, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_target = (rx, ry)

    if best_target is None:
        return [0, 0]

    tx, ty = best_target
    if (sx, sy) == (tx, ty):
        return [0, 0]

    curd = myd[sy][sx]
    # Take deterministic step that decreases distance to target most; tie-break by order in dirs
    best_step = (0, 0)
    best_val = myd[sy][sx]
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nd = myd[ny][nx]
        if nd < best_val:
            best_val = nd
            best_step = (dx, dy)
        elif nd == best_val:
            if dirs.index((dx, dy)) < dirs.index(best_step):
                best_step = (dx, dy)

    # If all steps blocked, stay
    if best_step == (0, 0) and myd[sy][sx] >= INF:
        return [0, 0]
    return [best_step[0], best_step[1]]