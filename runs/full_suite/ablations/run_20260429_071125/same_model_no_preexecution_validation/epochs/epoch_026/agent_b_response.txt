def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(start):
        x0, y0 = start
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

    distS = bfs((sx, sy))
    distO = bfs((ox, oy))

    best_t = None
    best_key = None
    for rx, ry in resources:
        ds = distS[rx][ry]; do = distO[rx][ry]
        if ds >= INF: 
            continue
        # Prefer resources we can reach significantly earlier; if tie, prefer closer to us.
        key = (do - ds, -ds, -abs(rx - sx) - abs(ry - sy), rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    cx, cy = w // 2, h // 2
    if best_t is None:
        target = (cx, cy)
    else:
        target = best_t

    tx, ty = target
    if distS[tx][ty] >= INF:
        # Fallback: go to closest reachable cell (by distance to us) toward center/opponent-avoid.
        best_move = [0, 0]
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            key = (abs(nx - cx) + abs(ny - cy), -distO[nx][ny], nx, ny)
            if best_key is None or key < best_key:
                best_key = key
                best_move = [dx, dy]
        return best_move

    # Choose move that minimizes our distance to target; tie-break: maximize opponent distance after move.
    best_move = [0, 0]
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds = distS[nx][ny]
        do = distO[nx][ny]
        key = (ds, -do, abs(nx - sx) + abs(ny - sy), nx, ny)
        if best_key is None or key < best_key:
            best_key = key
            best_move = [dx, dy]
    return best_move