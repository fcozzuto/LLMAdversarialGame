def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set((int(p[0]), int(p[1])) for p in obstacles_list)

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0):
            return dist
        dist[x0][y0] = 0
        qx = [x0]
        qy = [y0]
        qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx)
                    qy.append(ny)
        return dist

    dS = bfs(sx, sy)
    dO = bfs(ox, oy)

    res = [(int(p[0]), int(p[1])) for p in resources if valid(int(p[0]), int(p[1]))]
    res.sort()  # deterministic tie-break

    best = None
    best_key = None
    for rx, ry in res:
        ds = dS[rx][ry]
        if ds >= INF:
            continue
        do = dO[rx][ry]
        # Prefer: arrive first (max do-ds), then smallest ds, then smallest coord
        key = (do - ds, -ds, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        # Fallback: move toward center if possible
        cx, cy = w // 2, h // 2
        tx = 0 if sx == cx else (1 if sx < cx else -1)
        ty = 0 if sy == cy else (1 if sy < cy else -1)
        dx, dy = tx, ty
        if valid(sx + dx, sy + dy):
            return [dx, dy]
        # Try simple alternatives deterministically
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (0, 0)]:
            if valid(sx + dx, sy + dy):
                return [dx, dy]
        return [0, 0]

    rx, ry = best
    curd = dS[sx][sy]
    # Choose neighbor that strictly decreases distance to target; tie-break by deterministic direction order
    best_step = (0, 0)
    best_dist = INF
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = dS[nx][ny]
        if nd < best_dist and nd < curd:
            best_dist = nd
            best_step = (dx, dy)

    if best_dist < INF:
        return [best_step[0], best_step[1]]

    # If already at minimal/no decreasing (e.g., target unreachable in dist), pick deterministic valid move minimizing ds to target
    best_dist = INF
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            nd = dS[nx][ny]
            if nd < best_dist:
                best_dist = nd
                best_step = (dx, dy)
    return [best_step[0], best_step[1]]