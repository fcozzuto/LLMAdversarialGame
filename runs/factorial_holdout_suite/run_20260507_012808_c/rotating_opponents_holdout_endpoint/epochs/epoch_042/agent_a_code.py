def choose_move(observation):
    w = int(observation.get("grid_width", 8))
    h = int(observation.get("grid_height", 8))
    sx, sy = observation.get("self_position", (0, 0))
    ox, oy = observation.get("opponent_position", (0, 0))
    sx = int(sx); sy = int(sy); ox = int(ox); oy = int(oy)

    obstacles = set()
    for p in observation.get("obstacles") or []:
        if p and len(p) >= 2:
            x = int(p[0]); y = int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            x = int(r[0]); y = int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    deltas = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def bfs(start):
        inf = 10**9
        dist = [[inf]*h for _ in range(w)]
        x0, y0 = start
        if (x0, y0) in obstacles:
            return dist
        q = [(x0, y0)]
        dist[x0][y0] = 0
        qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in deltas:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    ds = bfs((sx, sy))
    do = bfs((ox, oy))

    # Candidate moves: deterministic order
    moves = []
    for dx, dy in deltas:
        nx, ny = sx + dx, sy + dy
        if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
            moves.append((dx, dy, nx, ny))

    best = None
    for dx, dy, nx, ny in moves:
        our_d_next = ds[nx][ny]
        # Expected advantage: favor states where we are closer than opponent to some resource.
        best_adv = -10**18
        best_our = 10**9
        for rx, ry in resources:
            us = ds[nx][ny] if (rx == nx and ry == ny) else ds[rx][ry]
            os = do[rx][ry]
            if us >= 10**9 or os >= 10**9:
                continue
            adv = os - us  # positive means we likely arrive first
            if adv > best_adv or (adv == best_adv and us < best_our):
                best_adv = adv
                best_our = us
        if best_adv == -10**18:
            # Fallback: move toward closest reachable resource from next
            best_our = 10**9
            for rx, ry in resources:
                us = ds[rx][ry]
                if us < best_our:
                    best_our = us
            best_adv = -best_our

        key = (best_adv, -best_our, -(abs(nx - ox) + abs(ny - oy)))
        if best is None or key > best[0]:
            best = (key, [dx, dy])

    return best[1]