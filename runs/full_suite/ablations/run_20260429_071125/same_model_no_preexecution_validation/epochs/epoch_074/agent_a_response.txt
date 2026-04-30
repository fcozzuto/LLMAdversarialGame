def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources") or []
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    moves = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles
    INF = 10**9

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0): return dist
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

    best = None
    best_key = None
    for p in resources:
        rx, ry = int(p[0]), int(p[1])
        if not valid(rx, ry): 
            continue
        ds, do = dS[rx][ry], dO[rx][ry]
        if ds >= INF:
            continue
        # Prefer resources we can beat opponent to (or at least tie), otherwise take only if it denies them.
        beat = (do - ds)
        if do >= INF:
            key = (2, ds, -rx, -ry)  # opponent unreachable -> strongly prefer
        else:
            # key[0]: whether we are earlier or tied; key[1]: advantage magnitude; key[2]: faster for us
            key = (0 if ds <= do else 1, -beat, ds, rx + ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry, ds)

    # If no resources reachable, move toward a generally open area: maximize distance from obstacles while staying valid.
    if best is None:
        best_move = (0, 0)
        best_score = -10**9
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            # local obstacle pressure: fewer blocked neighbors is better
            blocked = 0
            for ddx, ddy in moves:
                tx, ty = nx + ddx, ny + ddy
                if not valid(tx, ty): blocked += 1
            score = -(blocked) - (abs(nx - ox) + abs(ny - oy))
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    tx, ty, _ = best
    # Choose move that minimizes our BFS distance to the target; if tie, keep away from opponent and avoid dead-ends.
    curd = dS[sx][sy]
    best_move = (0, 0)
    best_tuple = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = d