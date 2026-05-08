def choose_move(observation):
    w = observation.get("grid_width", 8) or 8
    h = observation.get("grid_height", 8) or 8
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    if not (0 <= sx < w and 0 <= sy < h):
        return [0, 0]
    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def bfs(start):
        INF = 10**9
        x0, y0 = start
        dist = [[INF] * h for _ in range(w)]
        if not (0 <= x0 < w and 0 <= y0 < h) or (x0, y0) in obstacles:
            return dist
        dist[x0][y0] = 0
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in deltas:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    if not resources:
        tx, ty = (w - 1, h - 1) if sx < w // 2 else (0, 0)
        dx = 0 if tx == sx else (1 if tx > sx else -1)
        dy = 0 if ty == sy else (1 if ty > sy else -1)
        return [dx, dy]

    ds = bfs((sx, sy))
    do = bfs((ox, oy))

    best = None
    best_key = None
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        selfd = ds[rx][ry]
        oppd = do[rx][ry]
        if selfd >= 10**9:
            continue
        # Prefer resources we can reach sooner; also prefer where opponent is later.
        key = (oppd - selfd, -selfd, -abs(rx - sx) - abs(ry - sy))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        rx, ry = int(resources[0][0]), int(resources[0][1])
    else:
        rx, ry = best

    if (sx, sy) == (rx, ry):
        return [0, 0]

    best_move = (0, 0)
    best_score = None
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        selfd = ds[nx][ny]
        if selfd >= 10**9:
            continue
        oppd = do[nx][ny]  # approx: how quickly opponent could reach that vicinity
        score = (-selfd, oppd)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]