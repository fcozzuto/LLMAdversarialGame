def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obs_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obs_list)
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h

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

    best_r = None
    best_score = -10**18
    for r in resources:
        rx, ry = r[0], r[1]
        if not inb(rx, ry) or (rx, ry) in obstacles:
            continue
        md = myd[ry][rx]; od = opd[ry][rx]
        if md >= INF or od >= INF:
            continue
        score = (od - md) * 100 - md  # prioritize winning races, then closer
        if score > best_score or (score == best_score and (rx, ry) < (best_r[0], best_r[1])):
            best_score = score
            best_r = (rx, ry)

    if best_r is None:
        # fallback: move to reduce opponent's nearest distance
        target = (ox, oy)
        tx, ty = target
        curd = myd[sy][sx]
        best_move = (0, 0); best = curd
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                if myd[ny][nx] < best:
                    best = myd[ny][nx]; best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    rx, ry = best_r
    cur = myd[sy][sx]
    best_move = (0, 0); best_next = cur
    # greedy along our shortest path to chosen resource
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dnext = myd[ny][nx]
        if dnext <= best_next:
            # tie-break deterministically with lexicographic dx,dy order already in dirs
            if dnext < best_next or (dnext == best_next and (dx, dy) < best_move):
                best_next = dnext; best_move = (dx, dy)

    return [best_move[0], best_move[1]]