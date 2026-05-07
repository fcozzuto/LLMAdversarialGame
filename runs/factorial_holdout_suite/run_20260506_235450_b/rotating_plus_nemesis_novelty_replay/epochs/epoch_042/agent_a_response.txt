def choose_move(observation):
    w, h = observation["grid_width"], observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def valid(x, y):
        return inb(x, y) and (x, y) not in obstacles

    cand = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def bfs_from(px, py):
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        if not valid(px, py):
            return dist
        q = [(px, py)]
        dist[px][py] = 0
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if valid(nx, ny) and nd < dist[nx][ny]:
                        dist[nx][ny] = nd
                        q.append((nx, ny))
        return dist

    ds = bfs_from(sx, sy)
    do = bfs_from(ox, oy)

    INF = 10**9
    best_r = None
    best_key = None
    for rx, ry in resources:
        d1, d2 = ds[rx][ry], do[rx][ry]
        if d1 >= INF:
            continue
        # Prefer resources we can secure first or tie-break: larger (do - ds), then smaller ds
        key = (d2 - d1, -d1)
        if best_key is None or key > best_key:
            best_key = key
            best_r = (rx, ry)

    if best_r is None:
        # No reachable resources: drift toward center
        tx, ty = (w // 2, h // 2)
        best_move = (0, 0)
        best_md = None
        for dx, dy in cand:
            nx, ny = sx + dx, sy + dy
            if valid(nx, ny):
                md = abs(nx - tx) + abs(ny - ty)
                if best_md is None or md < best_md:
                    best_md = md
                    best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    tx, ty = best_r
    # Choose move that minimizes shortest-path distance to target; if tie, prefer improving contest
    best_move = (0, 0)
    best_tkey = None
    for dx, dy in cand:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd1 = ds[nx][ny]
        nd2 = do[nx][ny]
        # Primary: closest path to target (via dist-to-target already in ds at (tx,ty))
        # Secondary: reduce opponent access at same cell, tertiary: keep deterministic order
        tkey = (abs(nd1 - ds[tx][ty]), -(nd2), dx, dy)
        # Better if it reduces actual distance-to-target:
        tkey = (-ds[nx][ny] + ds[sx][sy], nd2, dx, dy)
        if best_tkey is None or tkey < best_tkey:
            best_tkey = tkey
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]