def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = int(observation["grid_width"]), int(observation["grid_height"])
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                obstacles.add((x, y))
    resources = []
    for p in (observation.get("resources") or []):
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in obstacles:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    def inb(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    moves = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def bfs(startx, starty):
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        if not inb(startx, starty):
            return dist
        q = [(startx, starty)]
        dist[startx][starty] = 0
        qi = 0
        while qi < len(q):
            x, y = q[qi]
            qi += 1
            d = dist[x][y] + 1
            for dx, dy in moves[:9]:
                nx, ny = x + dx, y + dy
                if inb(nx, ny) and d < dist[nx][ny]:
                    dist[nx][ny] = d
                    q.append((nx, ny))
        return dist

    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    opd = bfs(ox, oy)
    best_move = (0, 0)
    best_score = -10**18

    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not inb(nx, ny):
            continue
        myd = bfs(nx, ny)
        score = -10**18
        for rx, ry in resources:
            dme = myd[rx][ry]
            doe = opd[rx][ry]
            if dme >= 10**9 and doe >= 10**9:
                continue
            if doe >= 10**9:
                rel = 10**6 - dme
            elif dme >= 10**9:
                rel = -10**6
            else:
                rel = doe - dme  # prefer resources we can reach first
            # small tie-break: prefer center and avoid being "stuck" near obstacles (via distance)
            center_bias = -(abs(rx - cx) + abs(ry - cy)) * 0.01
            local = -(abs(dx) + abs(dy)) * 0.001
            s = rel + center_bias + local
            if s > score:
                score = s
        # fallback if all unreachable
        if score == -10**18:
            score = -abs(nx - cx) - abs(ny - cy) * 0.001
        # deterministic tie-break: lexicographic move preference close to original (0,0)
        if score > best_score or (score == best_score and (abs(dx) + abs(dy), dx, dy) < (abs(best_move[0]) + abs(best_move[1]), best_move[0], best_move[1])):
            best_score = score
            best_move = (dx, dy)

    return [int(best_move[0]), int(best_move[1])]