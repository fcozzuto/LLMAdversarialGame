def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles
    INF = 10**9
    def bfs(start):
        dist = [[INF]*h for _ in range(w)]
        x0, y0 = start
        if not valid(x0, y0): return dist
        dist[x0][y0] = 0
        q = [(x0, y0)]; qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist
    distS = bfs((sx, sy))
    distO = bfs((ox, oy))

    def cell_ok(x, y): return valid(x, y) and distS[x][y] < INF

    target = None
    best = -10**18
    for rx, ry in resources:
        if not valid(rx, ry) or distS[rx][ry] >= INF:
            continue
        dS = distS[rx][ry]; dO = distO[rx][ry]
        if dO >= INF: dO = 10**6
        # Prefer resources where we are closer than opponent; slight preference for nearer.
        sc = (dO - dS) * 1000 - dS
        if sc > best:
            best = sc; target = (rx, ry)

    if target is None:
        tx, ty = (w - 1)//2, (h - 1)//2
    else:
        tx, ty = target

    best_move = (0, 0); best_val = 10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny): 
            continue
        # Greedy toward target using BFS distance to avoid obstacles.
        d = distS[nx][ny]
        to_t = abs(nx - tx) + abs(ny - ty)
        # Also reduce chance of getting "stuck" behind opponent by mildly favoring squares where we are not farther.
        dO_here = distO[nx][ny]
        val = (distS[tx][ty] - d) * 1 + to_t * 3 + (0 if dO_here >= INF else dO_here) * 0.05
        if val < best_val:
            best_val = val; best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]