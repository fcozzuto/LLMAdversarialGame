def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
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

    best_target = None
    best_val = -INF
    best_ds = INF
    best_do = INF

    for tx, ty in resources:
        ds = distS[tx][ty]
        if ds >= INF:
            continue
        do = distO[tx][ty]
        # Prefer states where we arrive earlier; if do is INF, we can treat as big advantage.
        advantage = (do - ds) if do < INF else 20 - ds
        # Slightly prefer closer targets and deterministic tie-break by coordinates.
        val = advantage * 1000 - ds * 3
        if (val > best_val) or (val == best_val and (ds < best_ds or (ds == best_ds and (do < best_do or (do == best_do and (tx, ty) < best_target))))):
            best_val, best_ds, best_do, best_target = val, ds, do, (tx, ty)

    tx, ty = best_target if best_target is not None else resources[0]

    # If somehow current cell is invalid, move to a valid neighbor toward the target deterministically.
    if distS[sx][sy] >= INF:
        best = (INF, 0, 0)
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            # greedy manhattan-ish toward target for determinism
            dd = abs(nx - tx) + abs(ny - ty)
            key = (dd, dx, dy)
            if key < best:
                best = key
                best_move = [dx, dy]
        return best_move if 'best_move' in locals() else [0, 0]

    # Choose neighbor that minimizes our distance to the target; break ties by also reducing opponent distance.
    best = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nds = distS[nx][ny]
        if nds >= INF:
            continue
        ndo = distO[nx][ny]
        key = (nds, ndo if ndo < INF else 10**6, abs(nx - tx) + abs(ny - ty), dx, dy)
        if best is None or key < best:
            best = key
            best_move = [dx, dy]

    return best_move if 'best_move' in locals() else [0, 0]