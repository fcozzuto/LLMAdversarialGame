def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)

    def inb(x, y): return 0 <= x < w and 0 <= y < h
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def bfs(start):
        x0, y0 = start
        if not inb(x0, y0) or (x0, y0) in obstacles: return None
        dist = [[INF] * w for _ in range(h)]
        dist[y0][x0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x = qx[qi]; y = qy[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))
    if myd is None or opd is None:
        return [0, 0]

    if resources:
        best = None; best_score = -10**18
        for r in resources:
            rx, ry = r[0], r[1]
            if not inb(rx, ry) or (rx, ry) in obstacles: 
                continue
            md = myd[ry][rx]; od = opd[ry][rx]
            if md >= INF or od >= INF: 
                continue
            # Prefer taking sooner than opponent; if unclear, deny opponent and keep moving toward reachable targets.
            score = (od - md) * 1000 - md
            if score > best_score or (score == best_score and (rx, ry) < best):
                best_score = score; best = (rx, ry)
        if best is None:
            best = (w // 2, h // 2)
    else:
        best = (w // 2, h // 2)

    tx, ty = best
    # Greedy step toward target while staying valid; deterministically break ties by a fixed direction order.
    best_step = (0, 0); best_h = 10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        h = abs(nx - tx) + abs(ny - ty)
        # Slightly prefer reducing our BFS distance to avoid oscillations.
        my_next = myd[ny][nx]
        key = (h, my_next, dx, dy)
        cur_key = (best_h, myd[sy + best_step[1]][sx + best_step[0]] if inb(sx + best_step[0], sy + best_step[1]) else INF, best_step[0], best_step[1])
        if key < cur_key:
            best_h = h; best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]