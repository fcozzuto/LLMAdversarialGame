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

    best_t = None
    best_score = -INF
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not valid(rx, ry): 
            continue
        ds, do = dS[rx][ry], dO[rx][ry]
        if ds >= INF:
            continue
        # Prefer resources we reach sooner than opponent; otherwise prefer close ones.
        gain = do - ds
        score = gain * 1000 - ds
        if score > best_score:
            best_score = score
            best_t = (rx, ry)

    def choose_step_to(target):
        tx, ty = target
        cur_ds = dS[sx][sy]
        best = None
        best_key = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny): 
                continue
            nds = dS[nx][ny]
            # Must not increase ds too much; prioritize reduction.
            step_improve = cur_ds - nds
            # Secondary: reduce opponent's relative pressure.
            opp_nd = dO[nx][ny]
            # Also prefer moving toward target if ds tied.
            toward = -((abs(tx - nx) + abs(ty - ny)) + 0)
            key = (step_improve, -opp_nd, toward, -(dx * dx + dy * dy))
            if best_key is None or key > best_key:
                best_key = key
                best = (dx, dy)
        return best if best is not None else (0, 0)

    if best_t is not None:
        return list(choose_step_to(best_t))

    # No resources: deterministically drift toward center while avoiding obstacles.
    cx, cy = (w - 1) // 2, (h - 1) // 2
    best = (0, 0)
    best_d = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        d = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
        if best_d is None or d < best_d:
            best_d = d
            best = (dx, dy)
    return [best[0], best[1]]