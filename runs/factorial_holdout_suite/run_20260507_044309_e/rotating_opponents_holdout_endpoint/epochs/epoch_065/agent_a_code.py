def choose_move(observation):
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    obstacles = set()
    for p in observation.get("obstacles") or []:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    resources = []
    for r in observation.get("resources") or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def king_neighbors(x, y):
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    yield nx, ny

    def bfs(start):
        dist = [[10**9] * h for _ in range(w)]
        sx0, sy0 = start
        if (sx0, sy0) in obstacles:
            return dist
        dist[sx0][sy0] = 0
        q = [start]
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            nd = dist[x][y] + 1
            for nx, ny in king_neighbors(x, y):
                if nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    sd = bfs((sx, sy))
    od = bfs((ox, oy))
    cx, cy = (w - 1) * 0.5, (h - 1) * 0.5

    best = None
    for rx, ry in resources:
        ds, do = sd[rx][ry], od[rx][ry]
        if ds >= 10**9:
            continue
        if do >= 10**9:
            margin = 3  # treat unreachable opponent as strong win
        else:
            margin = do - ds  # positive if we arrive earlier
        center = -((rx - cx) * (rx - cx) + (ry - cy) * (ry - cy))
        key = (margin, -ds, center)
        if best is None or key > best[0]:
            best = (key, (rx, ry), ds, do)
    if best is None:
        return [0, 0]
    _, (tx, ty), _, _ = best

    moves = [(0, 0), (-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    bestm = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h):
            continue
        if (nx, ny) in obstacles:
            continue
        nd = sd[nx][ny]
        if nd >= 10**9:
            continue
        # Prefer reducing distance to target; if tied, prefer making opponent farther from target.
        opp_here = od[nx][ny]  # approximate "opponent distance if we were there" (stable, deterministic)
        key = (-nd, opp_here, -abs(tx - nx) - abs(ty - ny))
        if bestm is None or key > bestm[0]:
            bestm = (key, [dx, dy])
    return bestm[1] if bestm else [0, 0]