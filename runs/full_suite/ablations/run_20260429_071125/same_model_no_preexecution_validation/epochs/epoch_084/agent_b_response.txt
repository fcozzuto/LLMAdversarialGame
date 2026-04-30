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
        if not valid(x0, y0): return dist
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

    best = None
    best_val = -10**18
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not valid(rx, ry):
            continue
        ds = dS[rx][ry]
        do = dO[rx][ry]
        if ds >= INF and do >= INF:
            continue
        # Prefer resources we can reach earlier and earlier overall; also slight tie-break by opponent delay.
        val = (do - ds) * 100 - ds
        if do < INF:
            val += (do - ds <= 0) * -50  # discourage contested/immediate-loss targets
        if val > best_val:
            best_val = val
            best = (rx, ry)

    tx, ty = best if best is not None else (w // 2, h // 2)

    # Choose move that deterministically reduces distance to target; avoid increasing too much.
    curd = dS[sx][sy]
    best_move = (0, 0)
    best_rank = (10**18, 10**18, 10**18)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = dS[nx][ny]
        if nd >= INF:
            continue
        # Rank: primary nd, secondary (target vs current), tertiary lexicographic on move for determinism.
        rank = (nd, abs(nd - curd), abs(nx - tx) + abs(ny - ty))
        if rank < best_rank:
            best_rank = rank
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]