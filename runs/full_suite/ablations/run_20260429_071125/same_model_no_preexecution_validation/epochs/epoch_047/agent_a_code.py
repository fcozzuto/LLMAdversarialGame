def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    if not resources:
        return [0, 0]

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

    best_t = None
    best_key = None
    any_reach = False
    for rx, ry in resources:
        ds = distS[rx][ry]
        if ds >= INF:
            continue
        any_reach = True
        do = distO[rx][ry]
        # Prefer targets where we are closer than opponent; otherwise just get closest.
        # Key: (we_reach, we_ahead, advantage, -ds, deterministic tie by coords)
        ahead = 1 if do > ds else 0
        do_eff = do if do < INF else 10**6
        adv = do_eff - ds
        key = (1, ahead, adv, -ds, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best_t = (rx, ry)

    if not any_reach:
        # Move to reduce distance to opponent (or stay if no valid moves)
        best_move = [0, 0]
        best_val = -INF
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            v = -distO[nx][ny]
            if v > best_val:
                best_val = v
                best_move = [dx, dy]
        return best_move

    tx, ty = best_t
    # Choose move that minimizes our distance to target; break ties by maximizing opponent distance.
    chosen = [0, 0]
    best_val = -INF
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ds = distS[nx][ny]
        if ds >= INF:
            continue
        do = distO[nx][ny]
        ahead_now = 1 if do > ds else 0
        # Higher better:
        val = (ahead_now * 10**6) + (do - ds if do < INF else 10**6) * 10 - ds
        if val > best_val or (val == best_val and (dx, dy) < (chosen[0], chosen[1])):
            best_val = val
            chosen = [dx, dy]
    return chosen