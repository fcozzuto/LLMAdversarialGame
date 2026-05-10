def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", (0, 0)))
    ox, oy = map(int, observation.get("opponent_position", (0, 0)))
    obstacles = observation.get("obstacles") or []
    obs = {(int(p[0]), int(p[1])) for p in obstacles if p is not None and len(p) >= 2}
    def inside(x, y): return 0 <= x < w and 0 <= y < h
    def legal(x, y): return inside(x, y) and (x, y) not in obs
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def bfs_dist(startx, starty, goalx, goaly):
        if startx == goalx and starty == goaly: return 0
        INF = 10**9
        dist = [[INF] * w for _ in range(h)]
        if not legal(startx, starty): return INF
        qx, qy = [startx], [starty]
        head = 0
        dist[starty][startx] = 0
        while head < len(qx):
            x, y = qx[head], qy[head]
            head += 1
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
        return dist[goaly][goalx]

    self_role = (observation.get("self_role") or "").lower()
    pursuer = ("purs" in self_role) and ("evad" not in self_role) and ("evader" not in self_role)

    best_val = -10**9 if not pursuer else 10**9
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not legal(nx, ny): 
            continue
        d = bfs_dist(nx, ny, ox, oy)
        val = -d if pursuer else d
        if (pursuer and (d < best_val)) or ((not pursuer) and (d > best_val)):
            best_val = d
            best_move = (dx, dy)
        elif d == best_val:
            if (dx, dy) < best_move:
                best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]