def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []
    obs = set((p[0], p[1]) for p in obstacles)
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (not inb(x, y)) or ((x, y) in obs)

    if blocked(sx, sy) or blocked(ox, oy) or not resources:
        return [0, 0]

    INF = 10**9
    def bfs(start):
        if blocked(start[0], start[1]): return None
        dist = [[INF]*w for _ in range(h)]
        dist[start[1]][start[0]] = 0
        q = [(start[0], start[1])]
        qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if not blocked(nx, ny) and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    q.append((nx, ny))
        return dist

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))
    if myd is None or opd is None:
        return [0, 0]

    # Choose a reachable resource; prefer ones I can beat (strictly earlier if possible).
    best = None
    for rx, ry in resources:
        d1 = myd[ry][rx]; d2 = opd[ry][rx]
        if d1 >= INF: 
            continue
        # scoring: lower is better; first try to win, then closest.
        win = 0 if d2 == INF else (d1 - d2)
        score = (0 if (d2 == INF or d1 < d2) else 1, win, d1, (rx + ry))
        if best is None or score < best[0]:
            best = (score, (rx, ry))

    if best is None:
        return [0, 0]
    tx, ty = best[1]

    # Greedy step toward target with obstacle avoidance; deterministic tie-breaking.
    best_step = (INF, 0, 0)
    cx, cy = sx, sy
    for dx, dy in dirs:
        nx, ny = cx + dx, cy + dy
        if blocked(nx, ny):
            continue
        # Prefer moves that reduce shortest-path distance to target; if unknown, reduce dx/dy distance.
        dt = myd[ty][tx] - myd[ny][nx] if myd[ny][nx] < INF else INF
        heuristic = (0 if myd[ny][nx] < INF else 1, -dt, abs(tx - nx) + abs(ty - ny), dx, dy)
        if heuristic < best_step:
            best_step = heuristic
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]