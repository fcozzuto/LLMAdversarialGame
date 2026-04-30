def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = observation.get("obstacles", []) or []
    blocked = {(p[0], p[1]) for p in obstacles}
    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]
    INF = 10**9

    def bfs(start):
        dist = [[INF] * w for _ in range(h)]
        if not (0 <= start[0] < w and 0 <= start[1] < h):
            return dist
        if (start[0], start[1]) in blocked:
            return dist
        dist[start[1]][start[0]] = 0
        qx, qy = [start[0]], [start[1]]
        i = 0
        while i < len(qx):
            x, y = qx[i], qy[i]
            i += 1
            nd = dist[y][x] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    qx.append(nx)
                    qy.append(ny)
        return dist

    if not resources:
        return [0, 0]

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))

    best = None  # resource as tuple
    best_key = None
    for rx, ry in resources:
        dm = myd[ry][rx]
        do = opd[ry][rx]
        if dm >= INF and do >= INF:
            continue
        # Key: prioritize resources we can reach sooner; penalize those opponent reaches faster.
        key = (dm - do, dm, -do, rx, ry)
        if best_key is None or key < best_key:
            best_key = key
            best = (rx, ry)

    if best is None:
        return [0, 0]
    tx, ty = best

    # Choose move that most reduces distance to target; if equal, avoid moves that get closer to opponent's target faster.
    curd = myd[sy][sx]
    best_step = (0, 0)
    best_step_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            continue
        nd = myd[ny][nx]
        if nd >= INF:
            continue
        step_key = (nd, abs((opd[ny][nx] if opd[ny][nx] < INF else 10**6) - opd[ty][tx]), dx, dy)
        if best_step_key is None or step_key < best_step_key:
            best_step_key = step_key
            best_step = (dx, dy)

    return [int(best_step[0]), int(best_step[1])]