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
        if not inb(x0, y0) or (x0, y0) in obstacles:
            return dist
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

    target = None
    best_key = (-INF, INF)  # maximize margin, then minimize our arrival
    for rx, ry in resources:
        dm, do = myd[ry][rx], opd[ry][rx]
        if dm >= INF and do >= INF:
            continue
        margin = do - dm  # larger => we arrive earlier
        key = (margin, dm)
        if target is None or key > best_key:
            best_key = key
            target = (rx, ry)

    if target is None:
        tx, ty = w // 2, h // 2
        if myd[ty][tx] >= INF:
            target = (sx, sy)
        else:
            target = (tx, ty)

    rx, ry = target
    best_move = (0, 0)
    best_val = (-INF, INF, 0)  # (margin, our_dist, -step_order) for determinism

    order = {(dx, dy): i for i, (dx, dy) in enumerate(dirs)}  # deterministic tie-break

    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        dnext = myd[ny][nx]
        if dnext >= INF:
            continue
        # estimated arrival to target if we are at (nx,ny)
        dm_to = bfs((nx, ny))[ry][rx] if (rx != nx or ry != ny) else 0
        if dm_to >= INF:
            dm_to = myd[sy][sx]  # fallback; should be rare
        do_to = opd[ry][rx]  # opponent fixed
        margin = do_to - dm_to
        key = (margin, dm_to, -order[(dx, dy)])
        if best_move == (0, 0) or key > best_val:
            best_val = key
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]