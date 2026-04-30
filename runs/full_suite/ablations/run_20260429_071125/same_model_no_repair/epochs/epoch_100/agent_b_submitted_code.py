def choose_move(observation):
    sx, sy = observation["self_position"]
    ox, oy = observation["opponent_position"]
    w, h = observation["grid_width"], observation["grid_height"]
    obstacles = set()
    for p in (observation.get("obstacles") or []):
        if p and len(p) >= 2:
            obstacles.add((int(p[0]), int(p[1])))
    resources = []
    for p in (observation.get("resources") or []):
        if p and len(p) >= 2:
            t = (int(p[0]), int(p[1]))
            if t not in obstacles:
                resources.append(t)
    moves = [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    def safe(x, y):
        return 0 <= x < w and 0 <= y < h and (x, y) not in obstacles

    def cheb(x1, y1, x2, y2):
        dx = x1 - x2
        if dx < 0: dx = -dx
        dy = y1 - y2
        if dy < 0: dy = -dy
        return dx if dx > dy else dy

    def bfs_dist(start):
        INF = 10**9
        dist = [[INF] * h for _ in range(w)]
        if not safe(start[0], start[1]):
            return dist
        from collections import deque
        q = deque()
        dist[start[0]][start[1]] = 0
        q.append(start)
        while q:
            x, y = q.popleft()
            d = dist[x][y] + 1
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if safe(nx, ny) and d < dist[nx][ny]:
                        dist[nx][ny] = d
                        q.append((nx, ny))
        return dist

    cx, cy = (w - 1) // 2, (h - 1) // 2
    if not resources:
        best = None
        for dx, dy in moves:
            nx, ny = sx + dx, sy + dy
            if not safe(nx, ny):
                continue
            d0 = cheb(nx, ny, cx, cy)
            key = (d0, cheb(nx, ny, ox, oy), dx, dy)
            if best is None or key < best[0]:
                best = (key, [dx, dy])
        return best[1] if best else [0, 0]

    mydist0 = bfs_dist((sx, sy))
    opdists = bfs_dist((ox, oy))
    center_bias = cheb(sx, sy, cx, cy)

    best_move = None
    best_key = None
    for dx, dy in moves:
        nx, ny = sx + dx, sy + dy
        if not safe(nx, ny):
            continue
        mydist = bfs_dist((nx, ny))
        pos_adv = None
        best_target = None
        worst_target = None
        for rx, ry in resources:
            md = mydist[rx][ry]
            od = opdists[rx][ry]
            if md >= 10**9 or od >= 10**9:
                continue
            diff = od