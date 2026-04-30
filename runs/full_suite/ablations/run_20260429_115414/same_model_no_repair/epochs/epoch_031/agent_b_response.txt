def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    obs = set((p[0], p[1]) for p in obstacles)
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    INF = 10**9

    def bfs(start):
        x0, y0 = start
        dist = [[INF] * w for _ in range(h)]
        if not (0 <= x0 < w and 0 <= y0 < h) or (x0, y0) in obs:
            return dist
        dist[y0][x0] = 0
        qx = [x0]
        qy = [y0]
        i = 0
        while i < len(qx):
            x, y = qx[i], qy[i]
            i += 1
            nd = dist[y][x] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obs and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx)
                    qy.append(ny)
        return dist

    if not resources:
        return [0, 0]

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))

    # Choose resource where we have advantage; if none, choose closest to us.
    best = None
    best_key = None
    for rx, ry in resources:
        md = myd[ry][rx]
        od = opd[ry][rx]
        if md >= INF:
            continue
        if best is None:
            best = (rx, ry)
            best_key = (-(od - md), md, rx, ry)
        key = (-(od - md), md, rx, ry)  # maximize (md-od), then minimize md
        if key < best_key:
            best = (rx, ry)
            best_key = key

    if best is None:
        return [0, 0]
    tx, ty = best
    cur = myd[sy][sx]
    if cur >= INF:
        return [0, 0]

    # Move: pick a legal step that minimizes my distance to target; break ties by increasing opponent distance.
    best_step = (0, 0)
    best_step_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obs:
            continue
        md = myd[ny][nx]
        if md >= INF:
            continue
        od = opd[ny][nx]
        step_key = (md, -(od), dx * 0 + dy * 0)  # deterministic tie
        if best_step_key is None or step_key < best_step_key:
            best_step_key = step_key
            best_step = (dx, dy)

    # If all moves increase distance (rare), do a deterministic "escape" toward target direction.
    if best_step == (0, 0) and cur < myd[sy][sx]:
        pass
    return [int(best_step[0]), int(best_step[1])]