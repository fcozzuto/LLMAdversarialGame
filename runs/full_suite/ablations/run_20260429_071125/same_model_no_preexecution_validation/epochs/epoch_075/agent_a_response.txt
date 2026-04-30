def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources") or []
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    INF = 10**9

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0):
            return dist
        dist[x0][y0] = 0
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    dS = bfs(sx, sy)
    dO = bfs(ox, oy)

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def obstacle_pressure(x, y):
        c = 0
        for dx, dy in moves:
            if dx == 0 and dy == 0:
                continue
            nx, ny = x + dx, y + dy
            if (nx, ny) in obstacles:
                c += 1
        return c

    best = None
    best_key = None
    for p in resources:
        rx, ry = int(p[0]), int(p[1])
        if not valid(rx, ry):
            continue
        ds = dS[rx][ry]
        if ds >= INF:
            continue
        do = dO[rx][ry]
        if do >= INF:
            do = INF
        we_are_closer = do - ds
        # Prefer grabbing when we are ahead; penalize long waits; avoid highly obstacle-adjacent targets
        press = obstacle_pressure(rx, ry)
        key = (we_are_closer, -(press), -ds, rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        # Fallback: move to maximize distance from opponent while avoiding obstacle pressure
        bestm, bestv = (0, 0), -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            d = cheb(nx, ny, ox, oy)
            v = d - 2 * obstacle_pressure(nx, ny)
            if v > bestv:
                bestv = v
                bestm = (dx, dy)
        return [bestm[0], bestm[1]]

    tx, ty = best
    curd = dS[sx][sy]
    cur_press = obstacle_pressure(sx, sy)
    # Choose a step that decreases BFS distance to target; break ties by safety and not walking into opponent
    chosen = (0, 0)
    chosen_key = None
    for dx, dy in moves:
        nx, ny