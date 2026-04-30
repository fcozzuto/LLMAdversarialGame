def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    if not resources:
        return [0, 0]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def bfs(start):
        if not inb(start[0], start[1]) or start in obstacles:
            return None
        INF = 10**9
        dist = [[INF]*w for _ in range(h)]
        x0, y0 = start
        dist[y0][x0] = 0
        qx = [x0]; qy = [y0]; qi = 0
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
    myd = bfs((sx, sy))
    opd = bfs((ox, oy))
    if myd is None or opd is None:
        return [0, 0]

    best_val = 10**18
    best_targets = []
    INF = 10**9
    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in obstacles:
            continue
        md = myd[ry][rx]
        od = opd[ry][rx]
        if md >= INF:
            continue
        # Prefer resources I can reach sooner, but also deny ones the opponent is closer to.
        val = md - 0.85 * od + (0.02 * (rx + ry))
        if val < best_val - 1e-9:
            best_val = val
            best_targets = [(rx, ry, md, od)]
        elif abs(val - best_val) <= 1e-9:
            best_targets.append((rx, ry, md, od))
    if not best_targets:
        return [0, 0]
    # Deterministic tie-break: smaller my distance, then smaller od, then lexicographic.
    best_targets.sort(key=lambda t: (t[2], t[3], t[0], t[1]))
    tx, ty = best_targets[0][0], best_targets[0][1]

    # Choose next step that improves my distance to target while considering opponent pressure.
    def score_move(nx, ny):
        if (nx, ny) in obstacles or not inb(nx, ny):
            return 10**18
        my_to = myd[ny][nx] if myd[ny][nx] < INF else 10**8
        # Lower is better: reduce distance to target; slight penalty if opponent also improves.
        md = abs(nx - tx) + abs(ny - ty)
        od_improve = opd[ny][nx] if opd[ny][nx] < INF else 10**8
        return md + 0.25 * od_improve + 0.001 * my_to

    best_move = (0, 0)
    best_score = 10**18
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        sc = score_move(nx, ny)
        if sc < best_score - 1e-9:
            best_score = sc
            best_move = (dx, dy)
        elif abs(sc - best_score) <= 1e-9:
            if (dx, dy) < best_move:
                best_move = (dx, dy)
    return [int(best_move[0]), int(best_move[1])]