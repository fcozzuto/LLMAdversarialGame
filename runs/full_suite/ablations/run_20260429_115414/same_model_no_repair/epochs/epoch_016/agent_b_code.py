def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [w - 1, h - 1])
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inside(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def bfs(start):
        if not inside(start[0], start[1]):
            return None
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        dist[start[0]][start[1]] = 0
        q = [start]
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inside(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    if not resources:
        target = (w - 1, 0) if (sx + sy) % 2 == 0 else (0, h - 1)
        tx, ty = target
        dx = 0 if sx == tx else (1 if tx > sx else -1)
        dy = 0 if sy == ty else (1 if ty > sy else -1)
        return [dx, dy]

    myd0 = bfs((sx, sy))
    opd0 = bfs((ox, oy))
    if myd0 is None or opd0 is None:
        return [0, 0]

    INF = 10**9
    best = None
    best_key = None
    for rx, ry in resources:
        d1 = myd0[rx][ry]
        d2 = opd0[rx][ry]
        if d1 >= INF or d2 >= INF:
            continue
        # Prefer reachable sooner or lead in advance; deterministically break ties.
        key = (0 if d1 < d2 else 1, d1 - d2, d1, d2, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]

    tx, ty = best
    my_to_t = bfs((tx, ty))
    if my_to_t is None:
        return [0, 0]

    cur = my_to_t[sx][sy]
    best_move = (0, 0)
    best_val = cur
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inside(nx, ny):
            continue
        v = my_to_t[nx][ny]
        if v < best_val:
            best_val = v
            best_move = (dx, dy)
        elif v == best_val and (dx, dy) < best_move:
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]