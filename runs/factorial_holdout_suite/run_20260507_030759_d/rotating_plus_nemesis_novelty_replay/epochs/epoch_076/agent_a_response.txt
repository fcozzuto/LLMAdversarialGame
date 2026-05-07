def choose_move(observation):
    sp = observation.get("self_position", [0, 0]) or [0, 0]
    op = observation.get("opponent_position", [0, 0]) or [0, 0]
    sx, sy = int(sp[0]), int(sp[1])
    ox, oy = int(op[0]), int(op[1])
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)

    obstacles = set()
    for o in observation.get("obstacles", []) or []:
        if isinstance(o, (list, tuple)) and len(o) >= 2:
            obstacles.add((int(o[0]), int(o[1])))

    resources = []
    for r in observation.get("resources", []) or []:
        if isinstance(r, (list, tuple)) and len(r) >= 2:
            x, y = int(r[0]), int(r[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def bfs_from(start):
        dist = [[-1] * h for _ in range(w)]
        sx0, sy0 = start
        if (sx0, sy0) in obstacles:
            return dist
        q = [(sx0, sy0)]
        dist[sx0][sy0] = 0
        head = 0
        while head < len(q):
            x, y = q[head]
            head += 1
            nd = dist[x][y] + 1
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles and dist[nx][ny] < 0:
                        dist[nx][ny] = nd
                        q.append((nx, ny))
        return dist

    d_self = bfs_from((sx, sy))
    d_opp = bfs_from((ox, oy))

    best = None
    best_key = (-10**18, -10**18, -10**18)
    for rx, ry in resources:
        ds = d_self[rx][ry]
        do = d_opp[rx][ry]
        if ds < 0 or do < 0:
            continue
        # Win by arriving sooner than opponent; also strongly prefer positive advantage.
        key = (do - ds, -(ds), -(rx + ry * w))
        if key > best_key:
            best_key = key
            best = (rx, ry)
    if best is None:
        best = resources[0]

    rx, ry = best
    curd = d_self[rx][ry]
    if curd < 0:
        return [0, 0]

    moves = []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx, ny = sx + dx, sy + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles and d_self[nx][ny] >= 0:
                moves.append((d_self[nx][ny], dx, dy))
    if not moves:
        return [0, 0]

    # Choose deterministic move that minimizes distance to the target; break ties lexicographically.
    moves.sort(key=lambda t: (t[0], t[1], t[2]))
    _, dx, dy = moves[0]
    # If BFS distance didn't improve (rare), fall back to simple step toward target.
    if d_self[sx + dx][sy + dy] >= curd:
        dx = 0 if rx == sx else (1 if rx > sx else -1)
        dy = 0 if ry == sy else (1 if ry > sy else -1)
    return [int(dx), int(dy)]