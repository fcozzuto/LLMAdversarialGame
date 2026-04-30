def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    INF = 10**9
    def bfs(start):
        if not inb(start[0], start[1]) or start in obstacles: return None
        dist = [[INF]*w for _ in range(h)]
        dist[start[1]][start[0]] = 0
        qx = [start[0]]; qy = [start[1]]; qi = 0
        while qi < len(qx):
            x = qx[qi]; y = qy[qi]; qi += 1
            d = dist[y][x]
            nd = d + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx); qy.append(ny)
        return dist
    if not resources:
        return [0, 0]
    mydist = bfs((sx, sy)); opd = bfs((ox, oy))
    if mydist is None or opd is None:
        return [0, 0]

    best = None
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in obstacles: 
            continue
        md = mydist[ry][rx]; od = opd[ry][rx]
        if md >= INF: 
            continue
        # Prefer reachable earlier; then prefer closer to us; then farther from opponent
        key = (md, od, -od)
        if best is None or key < best[0]:
            best = (key, (rx, ry), md, od)
    if best is None:
        return [0, 0]
    tx, ty = best[1]

    cur_md = mydist[sy][sx]
    cur_od = opd[oy][ox]
    best_move = (0, 0)
    best_score = (INF, -INF, INF, INF)  # (new_md, -new_od, md_change, od_change)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        new_md = mydist[ny][nx] + mydist[ty][tx] - cur_md if mydist[ty][tx] < INF else mydist[ny][nx]
        # More reliable: use exact distance to target from neighbor
        if mydist[ny][nx] >= INF:
            continue
        new_md_to_t = mydist[ny][tx if tx < w else 0] if False else mydist[ty][nx]  # corrected below
    # Fix the above without extra lines by computing directly:
    best_score = (INF, -INF, INF, INF)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        new_md_to_t = mydist[ty][nx]
        new_od_to_t = opd[ty][nx] if opd[ty][nx] < INF else INF
        if new_md_to_t >= INF:
            continue
        md_change = new_md_to_t - mydist[ty][sx]
        od_change = new_od_to_t - opd[ty][ox]
        score = (new_md_to_t, -new_od_to_t, md_change, od_change)
        if score < best_score:
            best_score = score
            best_move = (dx, dy)

    return [best_move[0], best_move[1]]