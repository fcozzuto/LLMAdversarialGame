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
    best_key = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not valid(rx, ry): 
            continue
        ds = dS[rx][ry]
        if ds >= INF:
            continue
        do = dO[rx][ry]
        adv = do - ds  # positive means we are closer
        key = (-(adv < 1), -adv, ds)  # prioritize guaranteed/near advantage, then bigger adv, then closer
        if best_key is None or key < best_key:
            best_key, best_r = key, (rx, ry)

    if best_r is None:
        tx, ty = (w - 1) // 2, (h - 1) // 2
    else:
        tx, ty = best_r

    # Move greedily along our distance-to-target gradient
    curd = dS[tx][ty] if valid(tx, ty) else INF
    best_move = (0, 0)
    best_dist = curd
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = dS[nx][ny]
        # If target is reachable, prefer decreasing distance to it via path-length comparison
        if valid(tx, ty) and dS[tx][ty] < INF:
            # approximate: next step should reduce our distance-to-target (dist from next to target)
            # recompute local by comparing dS from next position to target using triangle inequality isn't available,
            # so use direct dist-to-target from next by running a tiny BFS when needed.
            pass
    # Tiny BFS from target to evaluate exact distance next->target deterministically
    # (still cheap on 8x8).
    dt = bfs(tx, ty) if valid(tx, ty) else None

    if dt is None or dt[sx][sy] >= INF:
        # Fallback: drift toward center while avoiding obstacles
        cx, cy = (w - 1) // 2, (h - 1) // 2
        tx, ty = cx, cy
        dt = bfs(tx, ty)

    best_move = (0, 0)
    best_d = dt[sx][sy]
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not