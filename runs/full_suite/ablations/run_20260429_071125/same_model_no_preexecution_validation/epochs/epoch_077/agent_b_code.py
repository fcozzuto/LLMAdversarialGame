def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources") or []
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles
    INF = 10**9

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

    dS = bfs(sx, sy)
    dO = bfs(ox, oy)

    resource_cells = []
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if valid(rx, ry):
            resource_cells.append((rx, ry))

    cur_best = INF
    if resource_cells:
        for rx, ry in resource_cells:
            ds = dS[rx][ry]
            if ds < cur_best:
                cur_best = ds

    # If no reachable resources, just move to maximize distance from opponent.
    def score_cell(x, y):
        if not valid(x, y):
            return (INF, -INF)
        if not resource_cells:
            # smaller is better: (min ds_to_resource, -min do_to_resource)
            return (INF, -(-1))  # neutral
        best_min_ds = INF
        best_min_adv = -INF
        for rx, ry in resource_cells:
            ds = dS[rx][ry]
            if ds == INF:
                continue
            do = dO[rx][ry]
            if ds < best_min_ds:
                best_min_ds = ds
                best_min_adv = do - ds
            elif ds == best_min_ds:
                best_min_adv = max(best_min_adv, do - ds)
        # Prefer cells that reduce own distance to resources (lower ds), and increase opponent delay (higher do-ds)
        return (best_min_ds, -best_min_adv)

    # Choose deterministic move among valid adjacent cells based on score.
    best_move = (0, 0)
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        # Key: how good the resulting cell is; also tie-break by fixed order already in moves.
        key = score_cell(nx, ny)
        # Additional tie-break: prefer staying within bounds and not increasing distance to nearest resource.
        if resource_cells and dS[nx][ny] != INF:
            nearest_ds = cur_best
        else:
            nearest_ds = cur_best
        full_key = (key[0], key[1], abs(nx - ox) + abs(ny - oy))
        if best_key is None or full_key < best_key:
            best_key = full_key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]