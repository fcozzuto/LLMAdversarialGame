def choose_move(observation):
    w = int(observation.get("grid_width") or 8)
    h = int(observation.get("grid_height") or 8)
    sp = observation.get("self_position") or [0, 0]
    op = observation.get("opponent_position") or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for p in observation.get("resources") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def ok(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def bfs(start):
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        if not ok(start[0], start[1]):
            return dist
        sx0, sy0 = start
        dist[sx0][sy0] = 0
        q = [(sx0, sy0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if ok(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    ds = bfs((sx, sy))
    do = bfs((ox, oy))

    # Choose resource with best relative advantage (closer for us, farther for opponent).
    target = None
    best = 10**18
    for tx, ty in resources:
        a = ds[tx][ty]
        b = do[tx][ty]
        if a >= 10**8:
            continue
        val = a - b  # lower is better for us
        if val < best:
            best = val
            target = (tx, ty)
    if target is None:
        target = ((w - 1) // 2, (h - 1) // 2) if ok((w - 1) // 2, (h - 1) // 2) else (sx, sy)

    tx, ty = target
    best_move = (0, 0)
    bestv = 10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not ok(nx, ny):
            continue
        v = ds[nx][ny]
        # Tie-break: avoid moving into tight proximity with opponent.
        # Chebyshev distance since diagonal allowed.
        mx = nx - ox
        if mx < 0: mx = -mx
        my = ny - oy
        if my < 0: my = -my
        md = mx if mx > my else my
        v2 = v * 1000 - md  # smaller v primary; larger opponent distance preferred
        if v2 < bestv:
            bestv = v2
            best_move = (dx, dy)

    dx, dy = best_move
    return [int(dx), int(dy)]