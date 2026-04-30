def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = map(int, observation.get("self_position", [0, 0]))
    ox, oy = map(int, observation.get("opponent_position", [0, 0]))
    obstacles = set((int(p[0]), int(p[1])) for p in (observation.get("obstacles") or []))
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    if not resources:
        # deterministic fallback: go toward center unless blocked
        cx, cy = (w - 1) // 2, (h - 1) // 2
        dx = 0 if sx == cx else (1 if sx < cx else -1)
        dy = 0 if sy == cy else (1 if sy < cy else -1)
        return [dx, dy]

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
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dxm, dym in moves:
                nx, ny = x + dxm, y + dym
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    distS = bfs(sx, sy)
    distO = bfs(ox, oy)

    # Choose the move that maximizes eventual advantage over opponent for reachable resources.
    best_score = -INF
    best_move = [0, 0]
    for dxm, dym in moves:
        nx, ny = sx + dxm, sy + dym
        if not valid(nx, ny):
            continue
        # Our distance to target from neighbor: distS[nx][ny] (already shortest from current to nx + 1 by BFS properties)
        # Compute best resource advantage from this neighbor.
        local_best = -INF
        for tx, ty in resources:
            ds = distS[nx][ny]
            do = distO[tx][ty]
            # If neighbor can't reach resource, ds may be INF; similarly do may be INF.
            # Prefer resources where we are at least not worse, strongly prefer those where we are closer.
            if distS[tx][ty] >= INF and ds >= INF:
                continue
            ds_t = distS[tx][ty]
            if ds_t >= INF or do >= INF:
                continue
            # Resource value: advantage plus slight bias to closer targets.
            score = (do - ds_t) * 10 - ds_t
            if score > local_best:
                local_best = score
        # Small tie-breaker: keep deterministic preference toward opponent's side (increasing x then y by sign)
        tie = (nx * 1000 + ny) * 1e-6
        score2 = local_best + tie
        if score2 > best_score:
            best_score = score2
            best_move = [dxm, dym]

    return [int(best_move[0]), int(best_move[1])]