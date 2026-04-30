def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**9

    def inb(x, y): return 0 <= x < w and 0 <= y < h

    def bfs(start):
        x0, y0 = start
        dist = [[INF] * w for _ in range(h)]
        if not inb(x0, y0) or (x0, y0) in obstacles: return dist
        dist[y0][x0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0

    best = None
    best_key = None
    for rx, ry in resources:
        if (rx, ry) in obstacles: continue
        md = myd[ry][rx]
        if md >= INF: continue
        od = opd[ry][rx]
        if od >= INF: od = INF
        # Higher is better: lead in race, then avoid giving opponent lead, then prefer nearer/central.
        lead = od - md  # positive means we arrive earlier
        dist_score = -md
        center_score = -((rx - cx) * (rx - cx) + (ry - cy) * (ry - cy))
        # Deterministic tie-break: lexicographic by coordinates.
        key = (lead, dist_score, center_score, -rx, -ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        # No reachable resource: move deterministically toward farthest reachable cell from opponent.
        target = (sx, sy)
        best_key = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                d = opd[ny][nx]
                key = (-d, nx, ny)
                if best_key is None or key > best_key:
                    best_key = key; target = (nx, ny)
        return [target[0] - sx, target[1] - sy]

    tx, ty = best
    # Move to neighbor that minimizes our BFS distance to target; tie-break: maximize opponent distance, then lexicographic.
    best_step = (0, 0)
    best_step_key = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles: continue
        k1 = myd[ny][nx]
        if k1 >= INF: continue
        k2 = opd[ny][nx]
        key = (-k1, k2, -abs(nx - tx) - abs(ny - ty), -nx, -ny)
        if best_step_key is None or key > best_step_key:
            best_step_key = key
            best_step = (dx, dy)
    return [best_step[0], best_step[1]]