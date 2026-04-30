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
        INF = 10**9
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
                if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in obstacles and nd < dist[nx][ny]:
                    dist[nx][ny] = nd
                    q.append((nx, ny))
        return dist

    dist_s = bfs((sx, sy))
    dist_o = bfs((ox, oy))

    best = None
    for rx, ry in resources:
        ds = dist_s[rx][ry]
        do = dist_o[rx][ry]
        if ds >= 10**8:
            continue
        # Prefer resources where we are closer than the opponent (advantage = do - ds)
        adv = do - ds
        cand = (adv, -ds, -rx, -ry)
        if best is None or cand > best[0]:
            best = (cand, (rx, ry))
    if best is None:
        return [0, 0]
    tx, ty = best[1]

    def passable(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    best_move = (None, None)
    best_score = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not passable(nx, ny):
            continue
        ds_next = dist_s[nx][ny]  # exact remaining distance in this static map
        # Also consider preventing opponent progress slightly by preferring moves that reduce their chance
        do_cur = dist_o[tx][ty]
        # Score: mainly minimize self distance, then maximize advantage (do_cur - ds_next), then deterministic tie-break
        score = (-(ds_next), (do_cur - ds_next), -(dx * dx + dy * dy), -nx, -ny)
        if best_score is None or score > best_score:
            best_score = score
            best_move = (dx, dy)

    if best_move[0] is None:
        return [0, 0]
    return [int(best_move[0]), int(best_move[1])]