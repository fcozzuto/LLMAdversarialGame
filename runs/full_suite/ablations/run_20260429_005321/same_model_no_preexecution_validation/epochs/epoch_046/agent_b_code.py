def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obst_list = observation.get("obstacles") or []
    obstacles = set((p[0], p[1]) for p in obst_list)

    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (x, y) in obstacles or not inb(x, y)

    if (sx, sy) in resources:  # already on a resource
        return [0, 0]
    if not resources:
        return [0, 0]

    INF = 10**9
    def bfs(start):
        x0, y0 = start
        if blocked(x0, y0):
            return None
        dist = [[INF] * w for _ in range(h)]
        dist[y0][x0] = 0
        qx = [x0]; qy = [y0]; qi = 0
        while qi < len(qx):
            x, y = qx[qi], qy[qi]; qi += 1
            nd = dist[y][x] + 1
            for dx, dy in dirs:
                nx, ny = x + dx, y + dy
                if not blocked(nx, ny) and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx); qy.append(ny)
        return dist

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))
    if myd is None or opd is None:
        return [0, 0]

    # Pick target resource that maximizes (opponent advantage) = opd - myd.
    best = None  # (score, myd, rx, ry)
    for rx, ry in resources:
        if blocked(rx, ry):
            continue
        a = myd[ry][rx]; b = opd[ry][rx]
        if a >= INF or b >= INF:
            continue
        score = (b - a) * 100 - a  # deterministic linear tie-break
        cand = (score, a, rx, ry)
        if best is None or cand > best:
            best = cand

    if best is None:
        return [0, 0]

    _, _, tx, ty = best
    if (sx, sy) == (tx, ty):
        return [0, 0]

    cur = myd[sy][sx]
    best_step = None  # (newdist, rx, ry)
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        nd = myd[ny][nx]
        if nd >= cur:  # mostly move toward target
            continue
        cand = (nd, nx, ny)
        if best_step is None or cand < best_step:
            best_step = cand

    if best_step is not None:
        _, nx, ny = best_step
        return [nx - sx, ny - sy]

    # Fallback: move to neighbor minimizing distance to target.
    best_step = None
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        nd = myd[ny][nx]
        cand = (nd, nx, ny)
        if best_step is None or cand < best_step:
            best_step = cand
    _, nx, ny = best_step
    return [nx - sx, ny - sy]