def choose_move(observation):
    w = int(observation["grid_width"])
    h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
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
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    distS = bfs(sx, sy)
    distO = bfs(ox, oy)

    if not resources:
        return [0, 0]

    best = None
    best_adv = -INF
    best_tieb = INF
    for tx, ty in resources:
        ds = distS[tx][ty]
        do = distO[tx][ty]
        if ds >= INF:
            continue
        # Prefer targets we can reach; prioritize where we are closer than opponent.
        adv = (do - ds) if do < INF else (ds * -2)
        tieb = ds
        if adv > best_adv or (adv == best_adv and tieb < best_tieb):
            best_adv = adv
            best_tieb = tieb
            best = (tx, ty)

    if best is None:
        return [0, 0]

    tx, ty = best

    # Choose among one-step valid moves: minimize our distance to target, but avoid letting opponent take it first.
    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds_next = distS[nx][ny]
        do_t = distO[tx][ty]
        ds_t = distS[tx][ty]
        # If we move closer in terms of ds_next, we improve. Keep opponent pressure as tie-break.
        score = (ds_next, -do_t if do_t < INF else 10**6)
        candidates.append((score, dx, dy))

    if not candidates:
        return [0, 0]

    candidates.sort(key=lambda t: (t[0][0], t[0][1], t[1], t[2]))
    return [int(candidates[0][1]), int(candidates[0][2])]