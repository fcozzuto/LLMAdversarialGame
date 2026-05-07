def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        try:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))
        except:
            pass

    resources = []
    for r in observation.get("resources", []) or []:
        try:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))
        except:
            pass

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def legal(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in blocked

    def bfs(start):
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        if not legal(start[0], start[1]):
            return dist
        q = [(start[0], start[1])]
        dist[start[0]][start[1]] = 0
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if legal(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    if not resources:
        return [0, 0]

    dist_s = bfs((sx, sy))
    dist_o = bfs((ox, oy))
    INF = 10**9
    candidates = []
    for rx, ry in resources:
        ds = dist_s[rx][ry]
        do = dist_o[rx][ry]
        if ds >= INF or do >= INF:
            continue
        key = (do - ds, -ds, rx, ry)
        candidates.append((key, (rx, ry)))
    if not candidates:
        return [0, 0]
    candidates.sort(key=lambda t: t[0], reverse=True)
    tx, ty = candidates[0][1]

    dist_t = bfs((tx, ty))
    best_move = (0, 0)
    best_val = 10**9
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        v = dist_t[nx][ny]
        if v < best_val or (v == best_val and (dx, dy) < best_move):
            best_val = v
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]