def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w = observation.get("grid_width", 8)
    h = observation.get("grid_height", 8)
    resources = observation.get("resources", []) or []
    obstacles = set(tuple(p) for p in (observation.get("obstacles", []) or []))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    INF = 10**9

    def bfs(start):
        dist = [[INF] * w for _ in range(h)]
        x0, y0 = start
        if not (0 <= x0 < w and 0 <= y0 < h) or (x0, y0) in obstacles:
            return dist
        q = [(x0, y0)]
        dist[y0][x0] = 0
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            nd = dist[y][x] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles and nd < dist[ny][nx]:
                    dist[ny][nx] = nd
                    q.append((nx, ny))
        return dist

    myd = bfs((sx, sy))
    opd = bfs((ox, oy))

    best_r = None
    best_key = None
    # Maximize advantage: (opponent distance - my distance), then prefer lower my distance, then deterministic tie on coordinates
    for rx, ry in resources:
        d1 = myd[ry][rx]
        d2 = opd[ry][rx]
        if d1 >= INF:
            continue
        if best_r is None:
            best_r = (rx, ry)
            best_key = (d2 - d1, -d1, -rx, -ry)
            continue
        if d2 >= INF:
            d2 = INF
        key = (d2 - d1, -d1, -rx, -ry)
        if key > best_key:
            best_key = key
            best_r = (rx, ry)

    rx, ry = best_r
    curd = myd[sy][sx]
    # Move to neighbor that decreases my distance to chosen resource; if none, move to best available cell by same objective
    best_move = (0, 0)
    best_val = -INF
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            continue
        nd = myd[ny][nx]
        if nd < INF:
            val = (opd[ry][rx] - nd)
            if nd < curd:
                val += 1000
            if val > best_val or (val == best_val and (dx, dy) < best_move):
                best_val = val
                best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]