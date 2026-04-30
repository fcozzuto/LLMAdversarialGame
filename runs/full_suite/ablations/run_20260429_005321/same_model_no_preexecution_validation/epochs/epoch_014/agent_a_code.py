def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set((p[0], p[1]) for p in (observation.get("obstacles") or []))
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    INF = 10**9

    def bfs(start):
        x0, y0 = start
        dist = [[INF] * w for _ in range(h)]
        if not inb(x0, y0) or (x0, y0) in obstacles:
            return dist
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

    best = None
    best_key = None
    any_reach = False
    for rx, ry in resources:
        md = myd[ry][rx]
        if md >= INF:
            continue
        any_reach = True
        od = opd[ry][rx]
        lead = od - md  # positive means we are closer or opponent farther
        # If we are tied/behind, still go to nearest reachable. Otherwise exploit lead strongly.
        key = (lead, -md, -(abs(rx - ox) + abs(ry - oy)))
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    if not any_reach:
        # Nowhere reachable: move deterministically to reduce distance to opponent for contest
        best_move = (0, 0)
        best_dist = None
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if not inb(nx, ny) or (nx, ny) in obstacles:
                continue
            d = (nx - ox) * (nx - ox) + (ny - oy) * (ny - oy)
            if best_dist is None or d < best_dist or (d == best_dist and (dx, dy) < best_move):
                best_dist = d; best_move = (dx, dy)
        return [best_move[0], best_move[1]]

    tx, ty = best
    if myd[ty][tx] == 0:
        # On a target: try to position for next closest resource; if none, move to deny by moving toward center
        target_best = None
        target_key = None
        for rx, ry in resources:
            md = myd[ry][rx]
            if md >= INF or (rx, ry) == (tx, ty):
                continue
            od = opd[ry][rx]
            lead = od - md
            key = (lead, -md, -(abs(rx - ox) + abs(ry - oy)))
            if target_key is None or key > target_key:
                target_key = key; target_best = (rx, ry)
        if target_best is None:
            # deterministic center-ish move
            cx, cy = (w - 1) // 2, (h - 1) // 2
            best_move = (0, 0); best_dist = None
            for dx, dy in dirs:
                nx, ny = sx + dx, sy + dy
                if not inb(nx, ny) or (nx, ny) in obstacles:
                    continue
                d = (nx - cx) * (nx - cx) + (ny - cy) * (ny - cy)
                if best_dist is None or d < best_dist or (d == best_dist and (dx, dy) < best_move):
                    best_dist = d; best_move = (dx, dy)
            return [best_move[0], best_move[1]]
        tx, ty = target_best

    # Choose next step that reduces my distance to target; tie