def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    resources = observation.get("resources") or []
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

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

    # Choose target resource where we are relatively closer than the opponent.
    if resources:
        best = None
        best_key = None
        for rx, ry in resources:
            ds = distS[rx][ry]; do = distO[rx][ry]
            if ds >= INF: 
                continue
            # Key: prefer where we are closer; also prefer faster overall and more "secure" advantage.
            adv = do - ds if do < INF else 10**6
            key = (adv, -ds, -abs(rx - (w-1)//2) - abs(ry - (h-1)//2), rx, ry)
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        tx, ty = best if best is not None else ((w-1)//2, (h-1)//2)
    else:
        tx, ty = (w-1)//2, (h-1)//2

    # Pick move that decreases our distance to target; if tied, prefer move that keeps opponent farther.
    best_mv = (0, 0); best_v = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny): 
            continue
        ds = distS[nx][ny]
        # opponent distance from current position after their turn is unknown; use static distO for tie-breaking.
        do = distO[nx][ny]
        # Also discourage staying if we can get closer.
        stay_pen = 1 if (dx == 0 and dy == 0) else 0
        v = (-(ds), (do if do < INF else -INF), -(abs(nx - tx) + abs(ny - ty)), -stay_pen, dx, dy)
        if best_v is None or v > best_v:
            best_v = v
            best_mv = (dx, dy)

    return [int(best_mv[0]), int(best_mv[1])]