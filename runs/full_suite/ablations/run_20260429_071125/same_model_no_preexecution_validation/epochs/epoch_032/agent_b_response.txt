def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    resources = observation.get("resources") or []
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0): return dist
        dist[x0][y0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x = qx[qi]; y = qy[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    distS = bfs(sx, sy)
    distO = bfs(ox, oy)

    best = None
    best_key = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not valid(rx, ry): 
            continue
        ds = distS[rx][ry]; do = distO[rx][ry]
        if ds >= INF: 
            continue
        # Prefer being strictly earlier; then maximize lead; then be closer
        key = (-(1 if ds < do else 0), -(ds == do and do != INF), -(do - ds), ds)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry, ds, do)

    # If no target, go toward center while avoiding obstacles
    if best is None:
        cx, cy = (w - 1) // 2, (h - 1) // 2
        candidates = []
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                candidates.append((abs(nx - cx) + abs(ny - cy), abs(nx - ox) + abs(ny - oy), dx, dy))
        candidates.sort()
        return [candidates[0][2], candidates[0][3]] if candidates else [0, 0]

    tx, ty = best[0], best[1]
    curd = distS[sx][sy]

    # Step that reduces our distance to target; break ties by not helping opponent
    best_step = (INF, INF, 0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny): 
            continue
        ds2 = distS[nx][ny]
        do2 = distO[nx][ny]
        if ds2 >= INF:
            continue
        # primary: reach sooner (lower ds2), secondary: keep opponent far (higher do2 - ds2 lead)
        lead = do2 - ds2
        key = (ds2, -lead, abs(nx - tx) + abs(ny - ty), 0 if (dx == 0 and dy == 0) else 1)
        # convert key to comparable tuple with deterministic tie-breaking
        if key < best_step[:3] + (best_step[2],):
            best_step = (key[0], key[1], dx, dy)

    dx, dy = best_step[2], best_step[3]
    if dx == 0 and dy == 0 and curd < INF:
        # ensure movement if possible when we can progress
        for ddx, ddy in moves:
            nx, ny = sx + ddx, sy + ddy
            if valid(nx, ny) and distS[nx][ny] < curd:
                return [ddx, ddy]
    return [dx, dy]