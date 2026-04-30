def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    obstacles = set(tuple(map(int, p)) for p in (observation.get("obstacles") or []))
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
        qx, qy = [x0], [y0]
        qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx)
                    qy.append(ny)
        return dist

    def cell_key(x, y):
        cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
        # prefer closer to center; then lexicographic for determinism
        return (-(abs(x - cx) + abs(y - cy)), x, y)

    def best_target(distS, distO):
        if not resources:
            return None
        best = None
        best_val = -INF
        for tx, ty in resources:
            ds = distS[tx][ty]
            if ds >= INF:
                continue
            do = distO[tx][ty]
            # Prefer cells we can reach sooner than opponent; slight preference for center-toward
            val = (do - ds) * 1000 - ds
            val += int(cell_key(tx, ty)[0])  # deterministic small tie guidance (negative magnitude)
            if val > best_val:
                best_val = val
                best = (tx, ty)
            elif val == best_val and cell_key(tx, ty) > cell_key(*best):
                best = (tx, ty)
        return best

    if not resources:
        dist = bfs(sx, sy)
        best_move = (0, 0)
        best_score = -INF
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            # drift to center
            cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
            score = -(abs(nx - cx) + abs(ny - cy))
            score -= dist[nx][ny] * 0.01
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    distS = bfs(sx, sy)
    distO = bfs(ox, oy)
    target = best_target(distS, distO)
    if target is None:
        # no reachable resource; go toward any reachable cell near center
        best_move = (0, 0)
        best_score = -INF
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            score = cell_key(nx, ny)
            score = (score[0], -distS[nx][ny], score[1], score[2])
            if score > best_score:
                best_score = score
                best_move = (dx, dy)
        return [int(best_move[0]), int(best_move[1])]

    tx, ty = target
    best_move = (0, 0)
    best_score = -INF
    for dx, dy in moves