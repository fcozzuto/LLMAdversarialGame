def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources") or []
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0): return dist
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

    dS = bfs(sx, sy)
    dO = bfs(ox, oy)

    best_r = None
    best_score = -10**18
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not valid(rx, ry): 
            continue
        ds, do = dS[rx][ry], dO[rx][ry]
        if ds >= INF and do >= INF:
            continue
        if ds >= INF:
            continue
        if do >= INF:
            do = 10 * w * h
        adv = do - ds  # positive if we arrive first
        score = adv * 100 - ds  # strongly prefer winning resources, then closer
        if score > best_score:
            best_score, best_r = score, (rx, ry)

    if best_r is None:
        # Fallback: move towards center while staying away from opponent
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        best_m, best_v = (0, 0), -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            dc = -((nx - cx) ** 2 + (ny - cy) ** 2)
            da = -(((nx - ox) ** 2 + (ny - oy) ** 2))
            v = dc * 2 + da
            if v > best_v:
                best_v, best_m = v, (dx, dy)
        return [int(best_m[0]), int(best_m[1])]

    rx, ry = best_r
    cur_ds = dS[rx][ry]
    # If already on target, just wait or make a move that doesn't lose the resource pursuit next.
    if sx == rx and sy == ry:
        return [0, 0]

    best_m, best_v = (0, 0), -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nds = dS[rx][ry]  # default for unreachable; overwritten if reachable from this move is hard, use dist from nx,ny
        nds = dS[nx][ny]  # for distance-to-self doesn't help; use direct lookup
        to_target = dS[nx][ny]  # placeholder removed below
        to_target = dS[rx][ry]  # wrong; fixed by using