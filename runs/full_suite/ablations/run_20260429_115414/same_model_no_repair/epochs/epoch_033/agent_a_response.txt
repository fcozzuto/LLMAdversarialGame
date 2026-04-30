def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = {(p[0], p[1]) for p in obstacles}

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    INF = 10**9

    def bfs(x0, y0):
        if not (0 <= x0 < w and 0 <= y0 < h) or (x0, y0) in blocked:
            return None
        dist = [[INF] * w for _ in range(h)]
        dist[y0][x0] = 0
        qx, qy = [x0], [y0]
        i = 0
        while i < len(qx):
            x, y = qx[i], qy[i]
            i += 1
            nd = dist[y][x] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx)
                    qy.append(ny)
        return dist

    myd = bfs(sx, sy)
    opd = bfs(ox, oy)
    if myd is None:
        return [0, 0]

    if not resources:
        # deterministic drift to center while respecting bounds/obstacles
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
                d = abs(nx - tx) + abs(ny - ty)
                if best is None or d < best[0] or (d == best[0] and (dx, dy) < best[1]):
                    best = (d, (dx, dy))
        return list(best[1]) if best else [0, 0]

    target = None
    best_key = None
    for rx, ry in resources:
        dm = myd[ry][rx]
        if dm >= INF:
            continue
        if opd is None:
            key = (INF, -dm, rx, ry)
        else:
            do = opd[ry][rx]
            if do >= INF:
                key = (INF, -dm, rx, ry)
            else:
                key = (do - dm, -dm, rx, ry)  # maximize advantage; then quicker; then deterministic
        if best_key is None or key > best_key:
            best_key = key
            target = (rx, ry)

    if target is None:
        # no reachable resource: move to any reachable neighbor that minimizes dist to center
        tx, ty = w // 2, h // 2
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
                d = abs(nx - tx) + abs(ny - ty)
                if best is None or d < best[0] or (d == best[0] and (dx, dy) < best[1]):
                    best = (d, (dx, dy))
        return list(best[1]) if best else [0, 0]

    rx, ry = target
    curd = myd[sy][sx]
    best_move = [0, 0]
    best_dist = curd
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked:
            d = myd[ny][nx]
            if d < best_dist or (d == best_dist and (dx, dy) < (best_move[0], best_move[1])):
                best_dist = d
                best_move = [dx, dy]
    # only accept moves that make progress toward target (dist decreases)
    if best_dist >= curd:
        # deterministic tie: choose move that most reduces manhattan