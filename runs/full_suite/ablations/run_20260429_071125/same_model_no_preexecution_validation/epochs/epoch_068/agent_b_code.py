def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    resources = observation.get("resources") or []
    obstacles = set(tuple(map(int, p)) for p in (observation.get("obstacles") or []))

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
            x, y = q[qi]
            qi += 1
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
    best_val = -INF
    for p in resources:
        rx, ry = map(int, p)
        ds = dS[rx][ry]
        if ds >= INF:
            continue
        do = dO[rx][ry]
        if do >= INF:
            do = ds + 1  # treat unreachable by opponent as favorable
        # Prefer resources we can reach earlier; otherwise contest.
        val = (1000 if ds <= do else 0) + (do - ds) * 3 - ds
        # Deterministic tie-break favor nearer-to-opponent-delay and then lexicographic.
        val = val * 1000 + (do - ds) * 10 + (-rx) - (-ry) * 0
        if val > best_val:
            best_val = val
            best = (rx, ry, ds, do)

    if best is not None:
        rx, ry = best[0], best[1]
    else:
        rx, ry = (w - 1) // 2, (h - 1) // 2

    # Choose the move that minimizes our BFS distance to (rx,ry); tie-break by maximizing alignment to target.
    best_move = (0, 0)
    best_dist = dS[rx][ry]
    tx, ty = rx - sx, ry - sy
    best_align = -INF
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        nd = dS[nx][ny]
        align = dx * tx + dy * ty
        if nd < best_dist or (nd == best_dist and (align > best_align or (align == best_align and (dx, dy) < best_move))):
            best_dist = nd
            best_align = align
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]