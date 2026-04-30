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

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def bfs(start):
        if not inb(start[0], start[1]):
            return None
        dist = [[-1] * h for _ in range(w)]
        q = [(start[0], start[1])]
        dist[start[0]][start[1]] = 0
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and dist[nx][ny] == -1:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    if not resources:
        return [0, 0]

    dself = bfs((sx, sy))
    dop = bfs((ox, oy))
    if dself is None or dop is None:
        return [0, 0]

    best = None
    for rx, ry in resources:
        ds = dself[rx][ry]
        if ds == -1:
            continue
        do = dop[rx][ry]
        if do == -1:
            do = ds + 5
        adv = do - ds
        key = (adv, -ds, -(abs(rx - ox) + abs(ry - oy)))
        if best is None or key > best[0]:
            best = (key, (rx, ry))

    if best is None:
        return [0, 0]

    _, (tx, ty) = best
    best_move = [0, 0]
    curd = dself[sx][sy]
    bestd = curd
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny) and dself[nx][ny] != -1:
            if dself[nx][ny] < bestd:
                bestd = dself[nx][ny]
                best_move = [dx, dy]
    if bestd == curd:
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        nx, ny = sx + dx, sy + dy
        if inb(nx, ny):
            return [dx, dy]
        return [0, 0]
    return best_move