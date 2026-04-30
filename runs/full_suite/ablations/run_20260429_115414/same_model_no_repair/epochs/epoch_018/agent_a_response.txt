def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    obstacles = observation.get("obstacles", [])
    resources = observation.get("resources", [])
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    obs = set((x, y) for x, y in obstacles)
    def bfs_dist(start):
        INF = 10**9
        dist = [[INF]*w for _ in range(h)]
        x0, y0 = start
        if not (0 <= x0 < w and 0 <= y0 < h) or (x0, y0) in obs:
            return dist
        q = [(x0, y0)]
        dist[y0][x0] = 0
        qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            d = dist[y][x] + 1
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs and d < dist[ny][nx]:
                        dist[ny][nx] = d
                        q.append((nx, ny))
        return dist
    if not resources:
        return [0, 0]
    myd = bfs_dist((sx, sy))
    opd = bfs_dist((ox, oy))
    best = None
    best_key = None
    for rx, ry in resources:
        d1 = myd[ry][rx]
        d2 = opd[ry][rx]
        if d1 >= 10**9:
            continue
        # Prefer resources we can reach sooner than opponent; otherwise pick closer/viable.
        key = (-(d2 - d1), d1, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)
    if best is None:
        return [0, 0]
    tx, ty = best
    cur = myd[sy][sx]
    moves = [(-1,-1),(0,-1),(1,-1),(-1,0),(0,0),(1,0),(-1,1),(0,1),(1,1)]
    best_move = (0, 0)
    best_mkey = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        nd = myd[ny][nx]
        if nd >= 10**9:
            continue
        # primary: reduce distance to target; secondary: increase advantage vs opponent at neighbor
        opp_nd = opd[ny][nx] if opd[ty][tx] < 10**9 else 10**9
        k = (nd - cur, nd, -opp_nd, nx, ny)
        if best_mkey is None or k < best_mkey:
            best_mkey = k
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]