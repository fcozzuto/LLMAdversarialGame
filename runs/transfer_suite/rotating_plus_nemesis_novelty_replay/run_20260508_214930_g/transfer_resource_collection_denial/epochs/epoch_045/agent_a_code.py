def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if inb(x, y) and (x, y) not in obs:
                res.append((x, y))
    if not res:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    dirs = moves

    def bfs(start):
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        x0, y0 = start
        if not inb(x0, y0) or (x0, y0) in obs:
            return dist
        dist[x0][y0] = 0
        q = [(x0, y0)]
        head = 0
        while head < len(q):
            x, y = q[head]
            head += 1
            d = dist[x][y] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obs and d < dist[nx][ny]:
                    dist[nx][ny] = d
                    q.append((nx, ny))
        return dist

    opp_dist = bfs((ox, oy))

    def best_adv(from_pos):
        sx2, sy2 = from_pos
        self_dist = bfs((sx2, sy2))
        best = (-10**9, 10**9)
        for rx, ry in res:
            sd = self_dist[rx][ry]
            od = opp_dist[rx][ry]
            if sd >= 10**9 or od >= 10**9:
                continue
            adv = od - sd
            # prefer higher advantage, then closer to that resource
            cand = (adv, sd)
            if cand[0] > best[0] or (cand[0] == best[0] and cand[1] < best[1]):
                best = cand
        return best

    best_move = [0, 0]
    best = (-10**9, 10**9)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        adv, sd = best_adv((nx, ny))
        if adv > best[0] or (adv == best[0] and sd < best[1]):
            best = (adv, sd)
            best_move = [dx, dy]
    return best_move