def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources") or []
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def valid(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not valid(x0, y0):
            return dist
        dist[x0][y0] = 0
        qx, qy, qi = [x0], [y0], 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    dS = bfs(sx, sy)
    dO = bfs(ox, oy)

    if resources:
        best = None
        bestv = -10**18
        for r in resources:
            tx, ty = int(r[0]), int(r[1])
            ds = dS[tx][ty]
            do = dO[tx][ty]
            if ds >= INF:
                continue
            # Prefer targets we can reach sooner than opponent; break ties by quicker pickup.
            v = (do - ds) * 1000 - ds
            if v > bestv:
                bestv = v
                best = (tx, ty)
        if best is None:
            tx, ty = w // 2, h // 2
        else:
            tx, ty = best
    else:
        tx, ty = w // 2, h // 2

    # Choose next step that decreases distance to target; if tie, increase opponent delay advantage.
    curr = dS[tx][ty]
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        dsn = dS[nx][ny]
        gain = curr - dsn
        do_n = dO[nx][ny]
        # Slightly prefer lines that keep opponent farther from the target cell.
        score = gain * 10000 + (dO[tx][ty] - dS[tx][ty]) - do_n * 0.01
        # Deterministic tie-break: lexicographic on move
        if score > best_score or (score == best_score and (dx, dy) < best_move):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]