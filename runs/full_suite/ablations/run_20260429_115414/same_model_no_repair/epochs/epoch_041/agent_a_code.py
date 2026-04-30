def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    blocked = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) == 2:
            blocked.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def bfs(start):
        dist = [[10**9] * h for _ in range(w)]
        x0, y0 = start
        if not inb(x0, y0):
            return dist
        dist[x0][y0] = 0
        q = [(x0, y0)]
        i = 0
        while i < len(q):
            x, y = q[i]
            i += 1
            nd = dist[x][y] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    if not resources:
        return [0, 0]

    ds = bfs((sx, sy))
    do = bfs((ox, oy))

    best = None
    for rx, ry in resources:
        if not inb(rx, ry):
            continue
        d1 = ds[rx][ry]
        d2 = do[rx][ry]
        if d1 >= 10**9:
            continue
        # Prefer resources we can reach much earlier than opponent; otherwise nearest.
        score = (d1 - d2) * 1000 + d1
        if best is None or score < best[0] or (score == best[0] and (d1 < best[1])):
            best = (score, d1, rx, ry)

    if best is None:
        # fall back to any reachable resource by our distance
        for rx, ry in resources:
            if inb(rx, ry) and ds[rx][ry] < 10**9:
                best = (ds[rx][ry], ds[rx][ry], rx, ry)
                break
        if best is None:
            return [0, 0]

    _, _, tx, ty = best
    curd = ds[sx][sy]
    beststep = (0, 0)
    bestnd = curd
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and ds[nx][ny] < bestnd:
            bestnd = ds[nx][ny]
            beststep = (dx, dy)

    # If already at target or no strictly better BFS neighbor, try greedy to reduce distance-to-target.
    if (sx, sy) == (tx, ty) or bestnd == curd:
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            return [dx, dy]
        # deterministic safe fallback: any move that is in-bounds and keeps BFS distance to target minimal
        bestd = ds[sx][sy]
        for ddx, ddy in dirs:
            nnx, nny = sx + ddx, sy + ddy
            if inb(nnx, nny) and ds[nnx][nny] <= bestd:
                bestd = ds[nnx][nny]
                beststep = (ddx, ddy)

    return [beststep[0], beststep[1]]