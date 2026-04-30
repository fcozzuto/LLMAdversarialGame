def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    s = observation.get("self_position") or [0, 0]
    o = observation.get("opponent_position") or [w - 1, h - 1]
    sx, sy = int(s[0]), int(s[1])
    ox, oy = int(o[0]), int(o[1])

    obstacles = set()
    for b in observation.get("obstacles") or []:
        if b and len(b) >= 2:
            bx, by = int(b[0]), int(b[1])
            if 0 <= bx < w and 0 <= by < h:
                obstacles.add((bx, by))

    resources = []
    for r in observation.get("resources") or []:
        if r and len(r) >= 2:
            rx, ry = int(r[0]), int(r[1])
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles:
                resources.append((rx, ry))
    if not resources:
        return [0, 0]

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def bfs(src):
        INF = 10**6
        dist = [[INF] * h for _ in range(w)]
        x0, y0 = src
        if not (0 <= x0 < w and 0 <= y0 < h) or (x0, y0) in obstacles:
            return dist
        dist[x0][y0] = 0
        q = [(x0, y0)]
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            nd = dist[x][y] + 1
            for dx, dy in moves:
                nx, ny = x + dx, y + dy
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles:
                    if nd < dist[nx][ny]:
                        dist[nx][ny] = nd
                        q.append((nx, ny))
        return dist

    distA = bfs((sx, sy))
    distB = bfs((ox, oy))

    best = None
    best_key = None
    for tx, ty in resources:
        dA = distA[tx][ty]
        dB = distB[tx][ty]
        if dA >= 10**6:
            continue
        # Prefer resources where we beat the opponent, but still consider absolute closeness.
        key = (dA - dB, dA + 0.1 * dB, tx, ty)
        if best_key is None or key < best_key:
            best_key = key
            best = (tx, ty)

    if best is None:
        return [0, 0]
    tx, ty = best

    candidates = []
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        dA2 = distA[nx][ny]
        dB2 = distB[nx][ny]
        # Main objective: approach target; Secondary: improve our relative position vs opponent.
        score = (abs(dA2 - (distA[tx][ty] - 1 if distA[tx][ty] > 0 else 0)), (dA2 - distB[nx][ny]), nx, ny, dx, dy)
        candidates.append((score, [dx, dy]))
    candidates.sort(key=lambda x: x[0])
    return candidates[0][1]