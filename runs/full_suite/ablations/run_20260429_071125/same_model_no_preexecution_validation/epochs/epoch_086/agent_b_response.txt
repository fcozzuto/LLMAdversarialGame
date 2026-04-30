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
        qx, qy = [x0], [y0]
        qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    dS = bfs(sx, sy)
    dO = bfs(ox, oy)

    cand = []
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if valid(rx, ry):
            ds, do = dS[rx][ry], dO[rx][ry]
            if ds < INF or do < INF:
                cand.append((rx, ry, ds, do))
    if not cand:
        bx, by = max([(valid(sx + dx, sy + dy) and (sx + dx, sy + dy) or (sx, sy)) for dx, dy in moves], key=lambda p: (-(abs(p[0]-ox)+abs(p[1]-oy))))
        return [int(bx - sx), int(by - sy)]

    good = [c for c in cand if c[2] <= c[3]]
    target_list = good if good else cand

    # Choose deterministic best target: minimize (ds - 0.6*do). Prefer reachable.
    def key(c):
        rx, ry, ds, do = c
        if ds >= INF: ds = INF
        if do >= INF: do = INF
        return (ds - 0.6 * do, ds + 0.05 * (abs(rx - ox) + abs(ry - oy)), rx, ry)
    rx, ry, _, _ = min(target_list, key=key)

    # Take one step that improves our distance to target; tie-break by maximizing distance to opponent
    best_moves = []
    best_ds = INF
    best_do = -INF
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            nx, ny = sx, sy
        ds = dS[nx][ny]  # deterministic dist from start, ok for tie
        d_to_target = dS[rx][ry]  # constant
        # primary: minimize distance from next position to target
        # approximated by using BFS from next is expensive; instead use heuristic: step closer by Chebyshev
        step_closer = max(abs(nx - rx), abs(ny - ry))
        if step_closer < best_ds or (step_closer == best_ds and dO[nx][ny] > best_do):
            best_ds = step_closer
            best_do = dO[nx][ny]
            best_moves = [(dx, dy)]
        elif step_closer == best_ds and dO[nx][ny] == best_do:
            best_moves.append((dx