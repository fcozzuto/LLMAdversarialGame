def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(start):
        dist = [[INF] * h for _ in range(w)]
        x0, y0 = start
        if not valid(x0, y0): return dist
        dist[x0][y0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x = qx[qi]; y = qy[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    def adj_obst_pen(x, y):
        p = 0
        for dx in (-1,0,1):
            for dy in (-1,0,1):
                if dx == 0 and dy == 0: 
                    continue
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) in obstacles:
                    p += 1
        return p

    if not resources or observation.get("remaining_resource_count", 0) <= 0:
        best = None; bestv = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            d = max(abs(nx - ox), abs(ny - oy))
            v = d*2 - adj_obst_pen(nx, ny)
            if v > bestv:
                bestv = v; best = (dx, dy)
        return list(best if best is not None else (0, 0))

    ds = bfs((sx, sy))
    do = bfs((ox, oy))
    res_list = [tuple(r) for r in resources if valid(r[0], r[1])]

    opp_near = INF
    for rx, ry in res_list: