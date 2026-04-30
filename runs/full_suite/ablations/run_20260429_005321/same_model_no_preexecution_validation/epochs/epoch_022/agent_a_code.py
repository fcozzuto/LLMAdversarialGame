def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = {(p[0], p[1]) for p in (observation.get("obstacles") or [])}
    dirs = [(-1,-1),(-1,0),(-1,1),(0,-1),(0,0),(0,1),(1,-1),(1,0),(1,1)]
    INF = 10**9

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h

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

    # Choose target resource maximizing arrival advantage; tie-break by faster self arrival.
    best = None
    best_key = (-10**18, 10**18)  # (opd - myd, -myd?) We'll compute with (gap, -myd) but store as max,min
    for rx, ry in resources:
        dm = myd[ry][rx]; do = opd[ry][rx]
        if dm >= INF or do >= INF:
            continue
        gap = do - dm  # higher means we arrive earlier by more (or opponent later)
        key = (gap, dm)  # maximize gap, then minimize dm
        if (best is None) or (key[0] > best_key[0]) or (key[0] == best_key[0] and key[1] < best_key[1]):
            best = (rx, ry); best_key = key

    if best is None:
        # fallback: move toward nearest corner/center (deterministic)
        tx, ty = (w // 2, h // 2)
    else:
        tx, ty = best

    # Pick move that strictly reduces distance to target if possible, else minimal increase.
    best_move = (0, 0)
    best_mdist = INF
    # Use BFS distance to target for robust pathing without full planning.
    tdist = bfs((tx, ty))
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny) or (nx, ny) in obstacles:
            continue
        d = tdist[ny][nx]
        if d < best_mdist or (d == best_mdist and (dx, dy) < best_move):
            best_mdist = d
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]