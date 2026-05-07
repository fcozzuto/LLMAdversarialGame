def choose_move(observation):
    w = int(observation.get("grid_width", 8) or 8)
    h = int(observation.get("grid_height", 8) or 8)
    sx, sy = observation.get("self_position", [0, 0]) or [0, 0]
    ox, oy = observation.get("opponent_position", [w - 1, h - 1]) or [w - 1, h - 1]
    sx, sy, ox, oy = int(sx), int(sy), int(ox), int(oy)

    blocked = set()
    for p in observation.get("obstacles", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h:
                blocked.add((x, y))

    resources = []
    for p in observation.get("resources", []) or []:
        if p and len(p) >= 2:
            x, y = int(p[0]), int(p[1])
            if 0 <= x < w and 0 <= y < h and (x, y) not in blocked:
                resources.append((x, y))
    if not resources:
        return [0, 0]

    dirs = [(-1, -1), (0, -1), (1, -1), (-1, 0), (0, 0), (1, 0), (-1, 1), (0, 1), (1, 1)]

    def bfs(start):
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        if 0 <= start[0] < w and 0 <= start[1] < h and start not in blocked:
            qx = [start[0]]
            qy = [start[1]]
            dist[start[0]][start[1]] = 0
            head = 0
            while head < len(qx):
                x, y = qx[head], qy[head]
                head += 1
                nd = dist[x][y] + 1
                for dx, dy in dirs:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in blocked and dist[nx][ny] > nd:
                        dist[nx][ny] = nd
                        qx.append(nx)
                        qy.append(ny)
        return dist

    sd = bfs((sx, sy))
    od = bfs((ox, oy))

    # Deterministic tie-breaking: smallest (x,y), then better score metrics
    best = None
    best_key = None
    for rx, ry in sorted(set(resources)):
        sdi = sd[rx][ry]
        odi = od[rx][ry]
        if sdi >= 10**9:
            continue
        if sdi == 0:
            return [0, 0]
        if odi >= 10**9:
            odi = 10**9
        # Prefer winning the race; otherwise deny opponent by increasing (opponent_dist - self_dist)
        race = odi - sdi  # bigger is better for us
        # Secondary: prefer closer to us, and avoid getting stuck by keeping path "direct"
        key = (race, -sdi, -abs(rx - sx) - abs(ry - sy), -abs(rx - ox) - abs(ry - oy), rx, ry)
        if best_key is None or key > best_key:
            best_key = key
            best = (rx, ry)

    tx, ty = best
    # Choose move that keeps greedy descent on our distance; deterministic by fixed dirs ordering
    cur = sd[sx][sy]
    next_move = (0, 0)
    next_dist = cur
    for dx, dy in dirs:
        nx, ny = sx + dx, sy + dy
        if not (0 <= nx < w and 0 <= ny < h) or (nx, ny) in blocked:
            continue
        nd = sd[nx][ny]
        if nd < next_dist:
            next_dist = nd
            next_move = (dx, dy)
    return [int(next_move[0]), int(next_move[1])]