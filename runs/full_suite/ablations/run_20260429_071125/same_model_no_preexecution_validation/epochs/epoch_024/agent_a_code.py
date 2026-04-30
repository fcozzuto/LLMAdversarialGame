def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**8

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(start):
        dist = [[INF] * h for _ in range(w)]
        x0, y0 = start
        if not valid(x0, y0):
            return dist
        dist[x0][y0] = 0
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    distS = bfs((sx, sy))
    distO = bfs((ox, oy))

    if not resources:
        # Defensive: move to maximize min(distO to resources-equivalent)
        best = (0, 0)
        bestv = (-INF, -INF)
        for dxm, dym in moves:
            nx, ny = sx + dxm, sy + dym
            if not valid(nx, ny):
                nx, ny = sx, sy
            od = distO[nx][ny]
            # also prefer moving slightly away from opponent
            away = abs(nx - ox) + abs(ny - oy)
            v = (od, away)
            if v > bestv:
                bestv = v; best = (dxm, dym)
        return [int(best[0]), int(best[1])]

    best_r = None
    best_key = None
    for rx, ry in resources:
        rx = int(rx); ry = int(ry)
        ds = distS[rx][ry]
        if ds >= INF: 
            continue
        do = distO[rx][ry]
        if do >= INF:
            do = INF
        # Prefer resources where we arrive earlier; break ties by closeness, then by opponent distance
        key = (ds - 0.75 * do, ds, -do)
        if best_key is None or key < best_key:
            best_key = key; best_r = (rx, ry)

    tx, ty = best_r if best_r is not None else (sx, sy)
    best_move = (0, 0)
    best_val = None
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not valid(nx, ny):
            nx, ny = sx, sy
        ns = distS[nx][ty] if tx is not None else INF
        if ns >= INF:
            continue
        # Try to get closer to target, and avoid letting opponent become earlier at target
        no = distO[nx][ty]
        # Also bias away from opponent position to reduce interference
        away = (abs(nx - ox) + abs(ny - oy))
        # Primary: minimize our remaining distance to target; Secondary: maximize opponent remaining distance
        val = (ns, -(no), -away)
        if best_val is None or val < best_val:
            best_val = val; best_move = (dxm, dym)

    return [int(best_move[0]), int(best_move[1])]