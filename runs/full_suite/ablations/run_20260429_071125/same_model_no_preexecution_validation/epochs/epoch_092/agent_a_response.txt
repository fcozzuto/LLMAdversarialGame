def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0])
    ox, oy = observation.get("opponent_position", [0, 0])
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)
    resources = observation.get("resources") or []
    obstacles_list = observation.get("obstacles") or []
    obstacles = set((int(p[0]), int(p[1])) for p in obstacles_list)

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
        qx, qy = [x0], [y0]
        qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if valid(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx)
                    qy.append(ny)
        return dist

    dS = bfs(sx, sy)
    dO = bfs(ox, oy)

    # Select a target resource that we can reach sooner (or at least contest) while staying away from opponent.
    best_r = None
    best_val = -10**18
    for r in resources:
        rx, ry = int(r[0]), int(r[1])
        if not inb(rx, ry) or (rx, ry) in obstacles:
            continue
        ds = dS[rx][ry]
        do = dO[rx][ry]
        if ds >= INF:
            continue
        # Higher is better; prefer smaller ds and larger advantage over opponent.
        val = (-ds) * 10 + (-do)
        if do < INF:
            val += (do - ds) * 3
        # Small deterministic bias toward resources nearer to center if tied.
        cx, cy = w // 2, h // 2
        val += -(abs(rx - cx) + abs(ry - cy)) * 0.01
        if val > best_val:
            best_val = val
            best_r = (rx, ry)

    # If no resource reachable, drift deterministically to keep distance from opponent.
    if best_r is None:
        cx, cy = w // 2, h // 2
        best = None
        best_s = -10**18
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not valid(nx, ny):
                continue
            # Prefer moving toward center while maximizing distance from opponent.
            dist_center = abs(nx - cx) + abs(ny - cy)
            dist_opp = max(abs(nx - ox), abs(ny - oy))
            score = -dist_center * 0.5 + dist_opp
            if score > best_s:
                best_s = score
                best = (dx, dy)
        if best is None:
            return [0, 0]
        return [best[0], best[1]]

    tx, ty = best_r
    # Choose move that best improves our distance to target, with tie-breaks: block opponent arrival, then avoid obstacles already handled.
    cur_ds = dS[sx][sy]
    best_move = (0, 0)
    best_score = -10**18
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not valid(nx, ny):
            continue
        ns = dS[nx][ny]
        no = dO[nx][ny]
        if ns >= INF:
            continue
        # Primary: reduce ds to target; Secondary: keep opponent farther from that cell; Tertiary: avoid getting closer to opponent.
        score = -(ns * 10) + (INF