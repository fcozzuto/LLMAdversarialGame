def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", (0, 0)))
    ox, oy = map(int, observation.get("opponent_position", (0, 0)))
    obstacles = observation.get("obstacles") or []
    obs = set()
    for p in obstacles:
        if p is not None and len(p) >= 2:
            obs.add((int(p[0]), int(p[1])))
    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def legal(x, y): return inside(x, y) and (x, y) not in obs
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    r = (observation.get("self_role", "") or "").lower()
    pursuer = ("purs" in r) or ("chaser" in r)

    def bfs_dist(startx, starty, goalx, goaly):
        if not legal(startx, starty):
            return 10**9
        if startx == goalx and starty == goaly:
            return 0
        INF = 10**9
        dist = [[INF] * w for _ in range(h)]
        dist[starty][startx] = 0
        qx = [startx]; qy = [starty]; head = 0
        while head < len(qx):
            x, y = qx[head], qy[head]; head += 1
            nd = dist[y][x] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if not legal(nx, ny):
                    continue
                if nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    if nx == goalx and ny == goaly:
                        return nd
                    qx.append(nx); qy.append(ny)
        return dist[goaly][goalx] if legal(goalx, goaly) else INF

    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny):
            continue
        d = bfs_dist(nx, ny, ox, oy)
        val = d if pursuer else -d
        cand = (val, dx, dy)  # deterministic tie-break
        if best is None or cand > best if not pursuer else cand < best:
            best = cand
    if best is None:
        return [0, 0]
    return [best[1], best[2]]