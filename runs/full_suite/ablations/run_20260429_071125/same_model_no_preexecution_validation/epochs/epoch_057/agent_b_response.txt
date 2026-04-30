def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = [tuple(map(int, p)) for p in (observation.get("resources") or [])]
    obstacles = set(tuple(map(int, p)) for p in (observation.get("obstacles") or []))
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

    if not resources:
        return [0, 0]

    distS = bfs(sx, sy)
    distO = bfs(ox, oy)

    best = None
    best_key = None
    for tx, ty in resources:
        ds = distS[tx][ty]
        if ds >= INF:
            continue
        do = distO[tx][ty]
        if do >= INF:
            do = INF
        adv = 0 if ds < do else 1
        # Prefer resources we can reach first; otherwise minimize our disadvantage.
        key = (adv, -((do - ds) if do < INF else -INF), ds, -abs(tx - ox) - abs(ty - oy))
        if best is None or key < best_key:
            best = (tx, ty); best_key = key

    if best is None:
        return [0, 0]
    tx, ty = best

    # Step to reduce distance to the chosen target (deterministic tie-break).
    curd = distS[sx][sy]
    best_step = (0, 0)
    best_step_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = distS[nx][ny]
        # Prefer strict improvement; then smaller remaining distance; then deterministic order.
        improve = 0 if nd < curd else 1
        key = (improve, nd, dx, dy)
        if best_step_key is None or key < best_step_key:
            best_step_key = key
            best_step = (dx, dy)
    return [int(best_step[0]), int(best_step[1])]