def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles
    INF = 10**8

    def bfs(start):
        x0, y0 = start
        if not valid(x0, y0):
            return [[INF]*h for _ in range(w)]
        dist = [[INF]*h for _ in range(w)]
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

    distS = bfs((sx, sy))
    distO = bfs((ox, oy))

    if resources:
        best = None
        best_val = -10**18
        for rx, ry in resources:
            if not valid(rx, ry):
                continue
            ds = distS[rx][ry]; do = distO[rx][ry]
            if ds >= INF or do >= INF:
                continue
            # Race advantage: prefer targets where opponent is farther; then pick smaller ds
            val = (do - ds) * 1000 - ds
            if val > best_val:
                best_val = val
                best = (rx, ry)
        if best is None:
            target = (sx, sy)
        else:
            target = best
    else:
        target = ((w-1)//2, (h-1)//2)

    tx, ty = target
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds_next = distS[nx][ny]
        # Encourage reaching target quickly while keeping/creating race advantage
        ds_t = distS[tx][ty]
        do_t = distO[tx][ty]
        # Also slight anti-opponent pressure: prefer positions where opponent is not closer to target than we are next
        do_next = distO[nx][ny]
        score = -ds_next * 3 + (do_t - (ds_t if ds_t < INF else 10**6)) - do_next * 0.1
        # If target is current, just maximize staying valid; ties by lexicographic move order
        if score > best_score:
            best_score = score
            best_move = (dx, dy)
    dx, dy = best_move
    return [int(dx), int(dy)]