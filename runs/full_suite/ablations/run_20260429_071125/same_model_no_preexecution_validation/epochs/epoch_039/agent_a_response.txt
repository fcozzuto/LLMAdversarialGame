def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    obstacles = set((int(p[0]), int(p[1])) for p in observation.get("obstacles") or [])
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**9

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0):
            return dist
        dist[x0][y0] = 0
        qx = [x0]
        qy = [y0]
        qi = 0
        while qi < len(qx):
            x = qx[qi]
            y = qy[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx)
                    qy.append(ny)
        return dist

    if not resources:
        return [0, 0]

    distO = bfs(ox, oy)

    best_move = (0, 0)
    best_val = -10**18

    # Tie-break deterministically by move order (as listed).
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
            dx, dy = 0, 0

        distS = bfs(nx, ny)
        best_r = -10**18
        for rx, ry in resources:
            ds = distS[rx][ry]
            if ds >= INF:
                continue
            do = distO[rx][ry]
            if do >= INF:
                do = INF
            # Primary: win the race to a resource (smaller ds than do).
            # Secondary: prioritize earlier capture, and prefer resources closer to us.
            race = (do - ds) if do < INF else ds * 0.5
            val = race * 100 - ds
            if val > best_r:
                best_r = val
        # If no reachable resource from this move, strongly de-prioritize.
        if best_r < -1e17:
            best_r = -1e18
        if best_r > best_val:
            best_val = best_r
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]