def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def bfs_from(st):
        sx0, sy0 = st
        INF = 10**9
        dist = [[INF]*h for _ in range(w)]
        if not valid(sx0, sy0): return dist
        dist[sx0][sy0] = 0
        q = [(sx0, sy0)]
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

    ds = bfs_from((sx, sy))
    do = bfs_from((ox, oy))

    if not resources:
        best = [0, 0]; bestk = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): continue
            d = abs(nx-ox); e = abs(ny-oy)
            cheb = d if d >= e else e
            key = (-cheb, abs(nx-(w-1)/2.0)+abs(ny-(h-1)/2.0), dx, dy)
            if bestk is None or key < bestk:
                bestk = key; best = [dx, dy]
        return best

    # Pick move that maximizes advantage to a target resource (distance lead), with small safety to avoid being too close to opponent.
    bestm = [0, 0]; bestk = None
    remaining = observation.get("remaining_resource_count", len(resources))
    tighten = 1.0 if remaining <= 4 else 0.6

    def cheb(a, b, c, d):
        dx = a - c; dx = -dx if dx < 0 else dx
        dy = b - d; dy = -dy if dy < 0 else dy
        return dx if dx > dy else dy

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny): continue
        # Evaluate local improvement by considering best reachable resource from the next cell.
        local_best = None
        for rx, ry in resources:
            if not valid(rx, ry): 
                continue
            dsn = 1 + (ds[sx][sy] - ds[sx][sy])  # keep deterministic no-op; ds already for current
            # Use precomputed distances but approximate next-cell self distance by 1 if moving closer in BFS metric.
            # If nx,ny cell is closer to the resource than current cell, use ds[nx][ny] else ds[sx][sy].
            curd = ds[sx][sy]; nextd = ds[nx][ny]
            dself = nextd if nextd < curd else curd
            dob = do[rx][ry]
            if dob >= 10**9 or dself >= 10**9:
                continue
            # Advantage: (opp_dist - self_dist), plus encourage shorter own path.
            adv = (dob - dself)
            # Safety: don't step into immediate opponent threat unless it secures a strong resource lead.
            danger = cheb(nx, ny, ox, oy)
            score = adv * 10 - dself * 1.2 - danger * (0.9 * tighten) + (1 if adv >= 1 else 0)
            key = (score, -adv, -dob,