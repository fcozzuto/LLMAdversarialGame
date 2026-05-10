def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def ok(x, y): return inb(x, y) and (x, y) not in obstacles
    if not resources:
        return [0, 0]

    def bfs_from(px, py):
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        if not ok(px, py):
            return dist
        dist[px][py] = 0
        q = [(px, py)]
        head = 0
        dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
        while head < len(q):
            x, y = q[head]; head += 1
            nd = dist[x][y] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if ok(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    sd = bfs_from(sx, sy)
    od = bfs_from(ox, oy)

    best = None
    best_score = None
    for rx, ry in resources:
        if not ok(rx, ry):
            continue
        self_d = sd[rx][ry]
        opp_d = od[rx][ry]
        if self_d >= 10**8:
            continue
        lead = opp_d - self_d
        score = (lead, -self_d, -opp_d)
        if best_score is None or score > best_score or (score == best_score and (rx, ry) < best):
            best_score = score
            best = (rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best

    deltas = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def choose_delta():
        bestm = (0, 0)
        bestk = None
        for dx, dy in deltas:
            nx, ny = sx + dx, sy + dy
            if not ok(nx, ny):
                continue
            k = (sd[nx][ny] - sd[tx][ty], abs(nx - tx) + abs(ny - ty), abs(nx - ox) + abs(ny - oy))
            # Prefer moves that reduce distance to target; deterministic tie-break by dx,dy ordering via tuple
            if bestk is None or k < bestk or (k == bestk and (dx, dy) < bestm):
                bestk = k
                bestm = (dx, dy)
        return bestm

    return list(choose_delta())