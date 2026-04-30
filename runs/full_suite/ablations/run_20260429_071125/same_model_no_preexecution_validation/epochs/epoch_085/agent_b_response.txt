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

    def best_resource():
        best = None
        best_score = -10**18
        for r in resources:
            rx, ry = int(r[0]), int(r[1])
            if not valid(rx, ry):
                continue
            ds, do = dS[rx][ry], dO[rx][ry]
            if ds >= INF and do >= INF:
                continue
            if ds >= INF:
                score = -10**12 - ds
            elif do >= INF:
                score = 10**12 - ds
            else:
                # Prefer targets we can beat (do-ds positive), but also prefer nearer overall.
                score = (do - ds) * 100 - ds
            if score > best_score:
                best_score = score
                best = (rx, ry, ds, do)
        return best

    target = best_resource()
    if target is None:
        # No useful resources: chase opponent
        tx, ty = ox, oy
        best_step = (0, 0)
        best_ds = dS[sx][sy]
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            if dS[nx][ny] < best_ds or best_step == (0, 0):
                best_ds = dS[nx][ny]
                best_step = (dx, dy)
        return [best_step[0], best_step[1]]

    rx, ry, ds, do = target
    # If we can't beat it (or it's a tie), switch to interception: move toward opponent if possible.
    if ds >= INF or (do < INF and (do - ds) <= 0):
        tx, ty = ox, oy
    else:
        tx, ty = rx, ry

    # Choose move that minimizes our distance to the chosen target.
    curd = dS[sx][