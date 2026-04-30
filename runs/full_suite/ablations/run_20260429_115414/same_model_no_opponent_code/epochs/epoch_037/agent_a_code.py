def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    obst = set()
    for p in observation.get("obstacles", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obst.add((x, y))

    res = []
    for p in observation.get("resources", []) or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obst:
                res.append((x, y))

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    def bfs_dist(x0, y0):
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        if (x0, y0) in obst:
            return dist
        dist[x0][y0] = 0
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            d = dist[x][y]
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
                    if dist[nx][ny] > d + 1:
                        dist[nx][ny] = d + 1
                        q.append((nx, ny))
        return dist

    sd = bfs_dist(sx, sy)
    od = bfs_dist(ox, oy)

    def best_target():
        if not res:
            return (w // 2, h // 2)
        best = None
        for rx, ry in res:
            ds = sd[rx][ry]
            do = od[rx][ry]
            if ds >= 10**9 and do >= 10**9:
                continue
            # Prefer resources we can reach sooner than opponent; tie-break deterministically.
            score = (do - ds) * 1000 - ds
            cand = (score, -do, -rx, -ry, rx, ry)
            if best is None or cand > best:
                best = cand
        if best is None:
            return (w // 2, h // 2)
        return (best[4], best[5])

    tx, ty = best_target()

    best_step = (10**9, 10**9, 0, 0)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obst:
            ds = sd[nx][ny]
            # move to reduce distance to target; small deterministic tie-break
            cand = (ds, abs(nx - tx) + abs(ny - ty), dx, dy)
            if cand < best_step:
                best_step = cand

    return [int(best_step[2]), int(best_step[3])]