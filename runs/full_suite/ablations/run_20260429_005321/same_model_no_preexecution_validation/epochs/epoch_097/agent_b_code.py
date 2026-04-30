def choose_move(observation):
    w = int(observation["grid_width"]); h = int(observation["grid_height"])
    sx, sy = int(observation["self_position"][0]), int(observation["self_position"][1])
    ox, oy = int(observation["opponent_position"][0]), int(observation["opponent_position"][1])
    obstacles = {(int(p[0]), int(p[1])) for p in (observation.get("obstacles") or [])}
    resources = [(int(p[0]), int(p[1])) for p in (observation.get("resources") or [])]
    dirs = [(dx, dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def free(x, y): return inb(x, y) and (x, y) not in obstacles

    def bfs(x0, y0):
        dist = [[INF] * h for _ in range(w)]
        if not free(x0, y0): return dist
        dist[x0][y0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]; qi += 1
            nd = dist[x][y] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if free(nx, ny) and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    myd = bfs(sx, sy)
    opd = bfs(ox, oy)

    # Pick a resource where we gain most time advantage; tie-break by our distance then coordinate.
    best = None
    best_key = None
    for rx, ry in resources:
        md = myd[rx][ry]; od = opd[rx][ry]
        if md >= INF and od >= INF:
            continue
        if od >= INF:  # we can reach, opponent can't
            key = (10**12, -md, rx, ry)
        elif md >= INF:
            key = (-10**12, md, rx, ry)
        else:
            key = (od - md, -md, rx, ry)
        if best_key is None or key > best_key:
            best_key = key; best = (rx, ry)

    if best is None:
        # Fallback: move toward opponent to contest space; deterministic tie-break by dx then dy
        tx, ty = ox, oy
        cur = (sx, sy)
        best_move = [0, 0]
        best_score = -10**18
        for dx, dy in dirs:
            nx, ny = cur[0] + dx, cur[1] + dy
            if not free(nx, ny): continue
            score = -((tx - nx) ** 2 + (ty - ny) ** 2)
            if score > best_score:
                best_score = score; best_move = [dx, dy]
        return best_move

    tx, ty = best
    # Choose move that decreases our distance to target; slight bias to avoid stepping next to an obstacle.
    def obstacle_penalty(x, y):
        p = 0
        for dx, dy in dirs:
            nx, ny = x + dx, y + dy
            if (nx, ny) in obstacles:
                p += 1
        return p

    best_move = [0, 0]
    best_val = -10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not free(nx, ny): continue
        d_before = myd[sx][sy]
        d_after = myd[nx][ny]
        if d_after >= INF:
            val = -10**9
        else:
            val = (d_before - d_after) * 1000000 - d_after - obstacle_penalty(nx, ny)
            # If we are tied on distance, prefer moves that also delay opponent reaching target.
            opp_d = opd[nx][ny] if (tx == nx and ty == ny) else opd[ox][oy]  # placeholder to keep deterministic scale
            # Better: use global opponent distance to target as tie-break.
            val += (opd[tx][ty] - myd[nx][ny]) * 2
        if val > best_val:
            best_val = val; best_move = [dx, dy]

    return best_move