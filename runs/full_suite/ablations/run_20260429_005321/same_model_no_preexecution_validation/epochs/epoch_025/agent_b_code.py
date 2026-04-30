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
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    q.append((nx, ny))
        return dist

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))

    # Choose resource we can reach and where we have timing advantage; otherwise aim for blocking by approaching nearest contested.
    best = None  # (advantage, -myd, rx, ry)
    for rx, ry in resources:
        dm = myd[ry][rx]; do = opd[ry][rx]
        if dm >= INF and do >= INF:
            continue
        if dm >= INF:
            key = (-INF, 0, rx, ry)
        else:
            adv = do - dm  # positive => arrive earlier
            key = (adv, -dm, rx, ry)
        if best is None or key > best:
            best = key

    if best is None:
        tx, ty = w // 2, h // 2
    else:
        _, _, tx, ty = best

    # Greedy step toward target with obstacle avoidance; deterministic tie-break.
    cx, cy = sx, sy
    options = []
    for dx, dy in dirs:
        nx, ny = cx + dx, cy + dy
        if inb(nx, ny) and (nx, ny) not in obstacles:
            options.append((myd[ny][nx] - 0.2 * abs(nx - tx) - 0.2 * abs(ny - ty), dx, dy, nx, ny))
    if not options:
        return [0, 0]
    options.sort(reverse=False)  # smaller is better due to constructed value
    # Deterministic: among equal value, smallest dx then dy is fine due to tuple ordering.
    _, dx, dy, _, _ = min(options, key=lambda t: (t[0], t[1], t[2], t[3], t[4]))
    return [int(dx), int(dy)]