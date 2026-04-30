def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles
    INF = 10**7

    def bfs(start):
        x0, y0 = start
        dist = [[INF]*h for _ in range(w)]
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

    def best_value(px, py):
        if not valid(px, py): return -INF
        best = -INF
        ds_here = distS[px][py]
        for rx, ry in resources:
            if not valid(rx, ry): 
                continue
            ds = distS[rx][ry]
            if ds >= INF: 
                continue
            do = distO[rx][ry]
            if do >= INF: 
                do = INF
            # Head-to-head priority: maximize (opponent later - me earlier), slight preference for closer
            adv = do - ds  # bigger is better
            val = adv*100 - ds*2
            if (px, py) == (rx, ry):
                val += 100000
            # If opponent is closer to the resource, still contest by moving to reduce its advantage
            if do < INF and ds > do:
                val += (do - ds)*20
            if val > best:
                best = val
        if best == -INF:
            # No reachable resources: move toward center-ish while avoiding opponent pressure
            best = -(abs(px - w//2) + abs(py - h//2)) - (abs(px - ox) + abs(py - oy))
        return best

    best_move = [0, 0]
    best_score = -INF
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        score = best_value(nx, ny)
        if score > best_score:
            best_score = score
            best_move = [dx, dy]
    return best_move