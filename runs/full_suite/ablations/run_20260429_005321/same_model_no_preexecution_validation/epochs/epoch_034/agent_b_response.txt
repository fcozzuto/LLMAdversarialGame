def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obst_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obst_list)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def bfs(start):
        x0, y0 = start
        if not inb(x0, y0) or (x0, y0) in obstacles:
            return None
        dist = [[INF] * w for _ in range(h)]
        dist[y0][x0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x = qx[qi]; y = qy[qi]; qi += 1
            d = dist[y][x] + 1
            if d > 50:
                continue
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and d < dist[ny][nx]:
                    dist[ny][nx] = d
                    qx.append(nx); qy.append(ny)
        return dist

    if not resources:
        return [0, 0]

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))
    if myd is None or opd is None:
        return [0, 0]

    best = None
    best_score = -INF
    res_sorted = sorted(resources, key=lambda p: (p[0], p[1]))
    for rx, ry in res_sorted:
        dm = myd[ry][rx]; do = opd[ry][rx]
        if dm >= INF or do >= INF:
            continue
        # Prefer resources I can get first; break ties by shorter distance and "edge" bias.
        lead = do - dm
        edge_bias = (min(rx, w - 1 - rx) + min(ry, h - 1 - ry)) * 0.01
        score = lead * 10 - dm - edge_bias
        if dm == do:
            score -= 0.5  # slightly prefer winning, but allow ties deterministically
        if score > best_score:
            best_score = score
            best = (rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best

    curd = myd[sy][sx]
    best_move = [0, 0]
    best_step_score = -INF
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        nd = myd[ny][nx]
        if nd >= INF:
            continue
        # Move that decreases my shortest path to target; also keep away from opponent a bit.
        progress = curd - nd
        opp_dist = opd[ny][nx]
        opp_term = 0 if opp_dist >= INF else opp_dist
        step_score = progress * 100 + opp_term * 0.05 - (abs(tx - nx) + abs(ty - ny)) * 0.01
        if step_score > best_step_score:
            best_step_score = step_score
            best_move = [dx, dy]

    return best_move if best_step_score > -INF else [0, 0]