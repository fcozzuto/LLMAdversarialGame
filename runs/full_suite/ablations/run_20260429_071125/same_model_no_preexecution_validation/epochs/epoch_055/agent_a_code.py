def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

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

    distS = bfs(sx, sy)
    distO = bfs(ox, oy)

    if resources:
        best = None
        best_key = None  # (adv, -opp_dist, self_dist, tx, ty)
        for tx, ty in resources:
            ds = distS[tx][ty]
            if ds >= INF: 
                continue
            do = distO[tx][ty]
            adv = do - ds
            key = (adv, -do, ds, tx, ty)
            if best is None or key > best_key:
                best = (tx, ty)
                best_key = key
        tx, ty = best
        curd = distS[sx][sy]
        best_move = (0, 0)
        best_score = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            nd = distS[nx][ny]
            # Prefer reducing distance; then prefer making opponent farther from target
            score = (-(nd if nd < INF else INF), -(distO[nx][ny] if distO[nx][ny] < INF else INF), abs(nx - tx) + abs(ny - ty), dx, dy)
            if best_score is None or score > best_score:
                best_score = score
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    # No resources: move to maximize separation and keep safe
    best_move = (0, 0)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dsep = abs(nx - ox) + abs(ny - oy)
        # Prefer not getting closer next turn; tie-break lexicographically toward center-ish
        score = (dsep, -abs(nx - (w - 1) / 2.0) - abs(ny - (h - 1) / 2.0), dx, dy)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]