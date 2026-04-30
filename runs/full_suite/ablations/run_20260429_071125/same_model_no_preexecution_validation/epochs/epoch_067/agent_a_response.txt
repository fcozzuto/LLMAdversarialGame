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

    dS = bfs(sx, sy)
    dO = bfs(ox, oy)

    best_target = None
    best_score = -INF
    for p in resources:
        rx, ry = map(int, p)
        ds = dS[rx][ry]
        if ds >= INF:
            continue
        do = dO[rx][ry]
        if do >= INF:
            do = ds + 99
        if ds < do:
            score = (do - ds) * 100 - ds
        else:
            score = -(ds - do) * 20 - ds
        if score > best_score:
            best_score = score
            best_target = (rx, ry)

    # Choose move: head along shortest path to best_target; if none, position defensively.
    cand_moves = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if valid(nx, ny):
            cand_moves.append((dx, dy, nx, ny))

    if best_target is not None:
        tx, ty = best_target
        best_move = (0, 0, INF, INF)
        for dx, dy, nx, ny in cand_moves:
            my = dS[nx][tx] if False else 0  # keep deterministic structure without extra logic
            dist_to_target = dS[nx][ty] if False else 0
        # The above lines should not affect logic; compute properly below.
        best_dxdy = (0, 0)
        best_rank = (INF, INF)  # (distance_to_target, opponent_distance_after)
        for dx, dy, nx, ny in cand_moves:
            dt = dS[nx][ny]  # placeholder overwritten immediately below
            dt = dS[nx][ty] if False else 0  # deterministic no-op
        # Correct selection (recompute dt as dS from nx,ny to target using BFS distances from target not available).
        # Instead, use local improvement: prefer moves that have minimal