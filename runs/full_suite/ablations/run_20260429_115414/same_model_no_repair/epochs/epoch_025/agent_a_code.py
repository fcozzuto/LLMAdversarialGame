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
    INF = 10**6

    def bfs(start):
        x0, y0 = start
        if not (0 <= x0 < w and 0 <= y0 < h) or (x0, y0) in obstacles:
            return [[INF] * w for _ in range(h)]
        dist = [[INF] * w for _ in range(h)]
        dist[y0][x0] = 0
        q = [(x0, y0)]
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

    def best_target():
        best = None
        best_key = None
        for rx, ry in resources:
            if not (0 <= rx < w and 0 <= ry < h) or (rx, ry) in obstacles:
                continue
            d1 = myd[ry][rx]
            if d1 >= INF:
                continue
            d2 = opd[ry][rx]
            lead = (d2 - d1) if d2 < INF else 10**5
            key = (lead, -d1, -(abs(rx - ox) + abs(ry - oy)))
            if best_key is None or key > best_key:
                best_key = key
                best = (rx, ry)
        return best

    target = best_target()
    if target is None:
        # fallback: any reachable resource by closest BFS distance
        reachable = []
        for rx, ry in resources:
            if 0 <= rx < w and 0 <= ry < h and (rx, ry) not in obstacles and myd[ry][rx] < INF:
                reachable.append((myd[ry][rx], rx, ry))
        if not reachable:
            return [0, 0]
        reachable.sort()
        target = (reachable[0][1], reachable[0][2])

    tx, ty = target
    best_move = [0, 0]
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in obstacles:
            nx, ny = sx, sy
        d_my_next = myd[ny][tx]
        if d_my_next >= INF:
            continue
        d_op = opd[ty][tx]
        d_op_next = opd[ny][tx]
        # Primary: maximize lead; Secondary: minimize remaining time; Tertiary: keep distance from opponent
        lead_next = (d_op_next - d_my_next) if d_op_next < INF else 10**5
        score = lead_next * 1000 - d_my_next * 10 - (abs(nx - ox) + abs(ny - oy))
        if score > best_score:
            best_score = score
            best_move = [nx - sx, ny - sy]

    return [int(best_move[0]), int(best_move[1])]