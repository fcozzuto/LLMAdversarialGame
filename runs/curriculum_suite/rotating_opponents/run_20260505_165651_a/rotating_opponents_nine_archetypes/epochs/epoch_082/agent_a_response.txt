def choose_move(observation):
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    resources = observation.get("resources") or []
    obstacles = observation.get("obstacles") or []

    obs = set()
    for p in obstacles:
        if isinstance(p, (list, tuple)) and len(p) >= 2:
            obs.add((p[0], p[1]))

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

    def bfs(start):
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        if not inb(start[0], start[1]) or (start[0], start[1]) in obs:
            return dist
        q = [start]
        dist[start[0]][start[1]] = 0
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            d = dist[x][y] + 1
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if inb(nx, ny) and (nx, ny) not in obs and d < dist[nx][ny]:
                        dist[nx][ny] = d
                        q.append((nx, ny))
        return dist

    valid_res = []
    for r in resources:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = r[0], r[1]
            if inb(x, y) and (x, y) not in obs:
                valid_res.append((x, y))
    if not valid_res:
        return [0, 0]

    dS = bfs((sx, sy))
    dO = bfs((ox, oy))

    best_targets = []
    best_margin = -10**9
    for tx, ty in valid_res:
        ds = dS[tx][ty]
        do = dO[tx][ty]
        if ds >= 10**8 or do >= 10**8:
            continue
        margin = do - ds  # positive means we arrive earlier
        if margin > best_margin:
            best_margin = margin
            best_targets = [(tx, ty)]
        elif margin == best_margin:
            best_targets.append((tx, ty))

    tx, ty = sorted(best_targets)[0]

    moves = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    best = (10**9, 10**9, 10**9)  # (ourDistNext, -oppNextDist, tieX/Y)
    best_move = (0, 0)
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obs:
            continue
        our_next = dS[nx][ny]
        opp_next = dO[tx][ty]  # constant; keep ordering stable
        # secondary: if tied, prefer moving toward target coords
        toward = abs(tx - nx) + abs(ty - ny)
        key = (our_next, -opp_next, toward)
        if key < best:
            best = key
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]