def choose_move(observation):
    w = observation["grid_width"]
    h = observation["grid_height"]
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    if not resources:
        return [0, 0]

    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    inb = lambda x, y: 0 <= x < w and 0 <= y < h

    def bfs(start, limit):
        if not inb(start[0], start[1]) or start in obstacles:
            return None
        INF = 10**9
        dist = [[INF] * w for _ in range(h)]
        x0, y0 = start
        dist[y0][x0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x = qx[qi]; y = qy[qi]; qi += 1
            d = dist[y][x]
            if d >= limit:
                continue
            nd = d + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    limit = w + h
    myd = bfs((sx, sy), limit)
    opd = bfs((ox, oy), limit)
    if myd is None:
        return [0, 0]

    INF = 10**9
    best_r = None
    best_score = -10**18

    for rx, ry in resources:
        if not inb(rx, ry) or (rx, ry) in obstacles:
            continue
        md = myd[ry][rx]
        if md >= INF:
            continue
        if opd is None:
            od = INF
        else:
            od = opd[ry][rx]
        # Prefer winning races; tie-break toward nearer resources and away from being stuck
        score = (od - md) * 10 - md
        # If we're already on a resource, take it
        if md == 0:
            score = 10**12
        if score > best_score:
            best_score = score
            best_r = (rx, ry)

    if best_r is None:
        return [0, 0]
    rx, ry = best_r

    best_step = (0, 0)
    best_step_val = INF
    # Move to neighbor that minimizes distance to chosen resource; if blocked, keep close to opponent race
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        v = myd[ny][nx]
        if v < best_step_val:
            best_step_val = v
            best_step = (dx, dy)

    # If resource not reachable in bfs limit, fall back to move toward best reachable resource by my distance only
    if best_step_val >= INF:
        target = None; best = INF
        for rx2, ry2 in resources:
            if inb(rx2, ry2) and (rx2, ry2) not in obstacles:
                d = myd[ry2][rx2]
                if d < best:
                    best = d; target = (rx2, ry2)
        if target is None:
            return [0, 0]
        tx, ty = target
        best_step = (0, 0); best_step_val = INF
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if inb(nx, ny) and (nx, ny) not in obstacles:
                v = myd[ny][nx]
                if v < best_step_val:
                    best_step_val = v; best_step = (dx, dy)

    dx, dy = best_step
    return [int(dx), int(dy)]