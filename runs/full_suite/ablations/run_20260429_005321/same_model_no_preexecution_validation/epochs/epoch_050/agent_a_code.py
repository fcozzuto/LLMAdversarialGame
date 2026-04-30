def choose_move(observation):
    w = observation["grid_width"]; h = observation["grid_height"]
    sx, sy = observation["self_position"]; ox, oy = observation["opponent_position"]
    resources = observation.get("resources") or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles") or []))
    dirs = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]
    def inb(x, y): return 0 <= x < w and 0 <= y < h
    def blocked(x, y): return (not inb(x, y)) or ((x, y) in obstacles)

    INF = 10**9
    def bfs(start):
        x0, y0 = start
        if blocked(x0, y0): return None
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
    if myd is None:
        return [0, 0]
    if not resources:
        return [0, 0]

    best = None
    best_key = None
    for rx, ry in resources:
        md = myd[ry][rx]
        if md >= INF:
            continue
        od = opd[ry][rx] if opd is not None else INF
        # Prefer resources where we are closer; also avoid unreachable for opponent.
        key = (-(od - md), md, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best

    curd = myd[sy][sx]
    best_move = [0, 0]
    best_nd = curd
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if blocked(nx, ny):
            continue
        nd = myd[ny][nx]
        if nd < best_nd:
            best_nd = nd
            best_move = [dx, dy]
    if best_move == [0, 0] and best_nd == curd:
        # If already at local minimum, take a deterministic legal move that doesn't increase distance.
        for dx, dy in dirs:
            nx, ny = sx + dx, sy + dy
            if blocked(nx, ny):
                continue
            nd = myd[ny][nx]
            if nd == curd:
                return [dx, dy]
    return best_move